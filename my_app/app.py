from shiny import App, ui, render, reactive
from utils import (
    register_business,
    notify_dropoff,
    verify_pickup,
    generate_test_pickup_code,
    validate_test_pickup_code,
    get_local_businesses,
    get_random_businesses_with_distances,
    get_fake_contract_text,
    is_valid_email,
    package_db, 
    move_package, 
    search_package, 
    initialize_mock_packages
)
from shiny.types import ImgData
from pathlib import Path
import asyncio

#App UI ---
app_ui = ui.page_fluid(
    ui.output_image("display_logo", inline=True),
    ui.br(),
    ui.h2("From the Parcel Encryption Squad", style="font-family: 'Brush Script MT', cursive; font-size: 32px; font-weight: bold; color: #4B0082;"),
    ui.p("A secure community-driven package pickup system.", style="font-family: 'Trebuchet MS', sans-serif; font-size: 16px; letter-spacing: 0.5px; color: #333;"),

  
    ui.h4("Are you a Customer or Package Retrieval Partner?"),
    ui.input_action_button("role_customer", "Customer", class_="btn-info"),
    ui.input_action_button("role_partner", "Package Retrieval Partner", class_="btn-secondary"),
    ui.br(),

    ui.div(
        ui.input_text("role_selected", label="0", value="0"),
        style="display: none"
    ),
    #used 0 because the null value didnt work -m
    ui.panel_conditional("input.role_selected == '0'",
        ui.card(
            ui.h3("📦 Welcome to Safe Drop!", style="color: #4a4a4a; font-weight: bold;"),
            ui.p("Created with care by the Parcel Encryption Squad™", style="font-style: italic; color: #6c757d;"),

            ui.p("This is a secure, community-powered system designed to keep your packages safe and your porch pirates unemployed.", 
                style="margin-top: 10px; font-size: 16px; line-height: 1.5;"),

            ui.tags.ul(
                ui.tags.li("👤 Are you a customer? Click the 'Customer' button to get a test pickup code and see nearby retrieval centers, no sign-in needed!", 
                        style="margin-bottom: 10px;"),
                ui.tags.li("🏪 Are you a package retrieval partner? Click 'Package Retrieval Partner' to register your business and manage deliveries like a boss.", 
                        style="margin-bottom: 10px;")
            ),

            ui.p("That’s it. No fluff. No fuss.", style="font-weight: 600; font-style: italic; margin-top: 15px;"),

            ui.p("💡 Fun fact: Najani, Meghan, and Kelvin didn’t just build a package system, they *engineered* the best pre-capstone project this side of campus. Sorry not sorry 🤷🏾‍♂️💅🏽",
                style="color: #198754; font-weight: bold; font-family: 'Comic Sans MS', cursive; font-size: 15px; margin-top: 20px;")
        )
    ),
    # --- Customer Section ---
    ui.panel_conditional("input.role_selected == 'customer'",
        ui.card(
            ui.h4("Test Customer Pickup"),
            ui.input_action_button("generate_code_btn", "Generate Test Pickup Code", class_="btn-warning"),
            ui.output_text("generated_code_display"),
            ui.input_text("pickup_code", "Enter Your Pickup Code"),
            ui.input_action_button("pickup_btn", "Verify Pickup", class_="btn-success"),
            ui.output_text("pickup_status")
        )
    ),
    ui.panel_conditional("output.pickup_status && output.pickup_status.includes('✅')",
        ui.card(
            ui.h4("Enter Your Address"),
            ui.input_text("user_address", "Your Address"),
            ui.input_action_button("save_address_btn", "Find Nearby Package Retrieval", class_="btn-primary"),
            ui.output_text("address_status")
        )
    ),
    ui.panel_conditional("output.address_status && output.address_status.includes('✅')",
        ui.card(
            ui.h4("Nearby Package Retrieval Centers"),
            ui.output_ui("retrieval_dropdown"),
            ui.output_text("retrieval_center_status"),
            ui.input_action_button("lock_center_btn", "Lock In This Center", class_="btn-success"),
            ui.output_text("thank_you_message")
        )
    ),


    # --- Partner Section ---
    ui.panel_conditional("input.role_selected == 'partner'",
        ui.card(
            ui.input_radio_buttons("partner_action", "Choose an option:",
                choices=["Register a new business", "Sign in to existing business"]
            )
        ),

        # Registration Form
        ui.panel_conditional("input.partner_action == 'Register a new business'",
            ui.card(
                ui.h4("Business Sign Up Form"),
                ui.input_text("signup_name", "Business Name"),
                ui.output_ui("name_error"),

                ui.input_text("signup_address", "Business Address"),
                ui.output_ui("address_error"),

                ui.input_text("signup_email", "Email"),
                ui.output_ui("email_warning_text"),

                ui.input_password("signup_password", "Password"),
                ui.input_password("signup_password_confirm", "Retype Password"),
                ui.output_ui("password_warning_text"),

                ui.input_text("signup_employee_id", "Employee ID"),
                ui.output_ui("employee_id_error"),

                ui.input_select("signup_role", "Your Role in the Company:",
                    choices=["CEO", "President", "Owner", "Manager", "Supervisor", "Other"]
                ),
                ui.output_ui("role_error"),

                ui.input_action_button("save_signup_info", "Save Information", class_="btn-primary"),
                ui.output_text("signup_save_status")
            )
        ),

        ui.panel_conditional("output.signup_save_status == '✅ Info saved'",
            ui.card(
                ui.h4("Agreements and Licensing"),
                ui.output_ui("contract_text"),
                ui.input_checkbox("contract_agree", "I agree to the terms and conditions"),
                ui.input_action_button("final_register_btn", "Finalize Business Registration", class_="btn-success"),
                ui.output_text("final_registration_status")
            )
        ),

        # Sign in to existing business
        ui.panel_conditional("input.partner_action == 'Sign in to existing business'",
            ui.card(
                ui.h4("Sign In to Existing Business"),
                ui.output_text("reminder_credentials"),
                ui.p("(You can use the sample login — Email: sample@biz.com | Password: sample123)"),
                ui.input_text("partner_signin_email", "Email"),
                ui.input_password("partner_signin_password", "Password"),
                ui.input_action_button("partner_signin_btn", "Sign In", class_="btn-success"),
                ui.output_text("partner_signin_status"),
                ui.output_text("partner_signin_success_info")
            )
        ),

    # --- Package Management Dashboard (Visible After Partner Sign-In) ---
        ui.panel_conditional("input.partner_action == 'Sign in to existing business' && output.partner_signin_status.includes('✅')",
            ui.card(
                ui.h4("📦 Package Management Dashboard"),
                ui.input_text("search_query", "Search by name or tracking ID"),
                ui.input_action_button("search_btn", "Search", class_="btn-info"),
                ui.output_ui("search_results")
            ),
            ui.card(
                ui.h4("🚚 Packages On the Way"),
                ui.output_ui("on_the_way_list")
            ),
            ui.card(
                ui.h4("📍 Ready for Pickup"),
                ui.output_ui("ready_for_pickup_list")
            ),
            ui.card(
                ui.h4("✅ Picked Up in the Last 24 Hours"),
                ui.output_ui("picked_up_list")
            )
        )

    )
)

# --- Server logic ---
def server(input, output, session):
    signin_result = reactive.Value("")
    passwords_match = reactive.Value(True)
    generated_code = reactive.Value("")
    pickup_result = reactive.Value("")
    user_address = reactive.Value("")
    business_dropdown_choices = reactive.Value([])
    temp_signup_info = reactive.Value({})
    email_is_valid = reactive.Value(True)
    password_is_valid = reactive.Value(True)
    signup_errors = reactive.Value({})
    local_businesses = get_local_businesses()
    final_status_message = reactive.Value("")
    signin_result = reactive.Value("")
    partner_signin_status_val = reactive.Value("")
    partner_signin_success_val = reactive.Value("")
    button_clicks_ready = reactive.Value({})
    button_clicks_picked = reactive.Value({})
    thank_you_msg = reactive.Value("")




    @reactive.Effect
    @reactive.event(input.role_customer)
    def _():
        generated_code.set("")
        pickup_result.set("")
        user_address.set("")
        business_dropdown_choices.set([])
        temp_signup_info.set({})
        session.send_input_message("role_selected", {"value": "customer"})

    @reactive.Effect
    @reactive.event(input.role_partner)
    def _():
        generated_code.set("")
        pickup_result.set("")
        user_address.set("")
        business_dropdown_choices.set([])
        temp_signup_info.set({})
        session.send_input_message("role_selected", {"value": "partner"})

    @reactive.Effect
    @reactive.event(input.generate_code_btn)
    def generate_test_code():
        code = generate_test_pickup_code()
        generated_code.set(code)

    @reactive.Effect
    @reactive.event(input.pickup_btn)
    def handle_pickup():
        entered_code = input.pickup_code()
        if validate_test_pickup_code(entered_code, generated_code.get()):
            pickup_result.set(f"✅ Pickup verified for code: {entered_code}")
        else:
            pickup_result.set("❌ **Sorry, that's not a valid pickup code. Please try again!**")

    @reactive.Effect
    @reactive.event(input.save_address_btn)
    def save_address():
        if input.role_selected() != "customer":
            return
        address = input.user_address()
        if address:
            user_address.set(address)
            business_dropdown_choices.set(get_random_businesses_with_distances(local_businesses))
        else:
            business_dropdown_choices.set([])
    @reactive.Effect
    @reactive.event(input.signin_btn)
    def handle_signin():
        email = input.signin_email()
        password = input.signin_password()
        
        # Placeholder logic — replace with real check later session.send_custom -whatever only sends it in the actual cmd line
        if email == "test@email.com" and password == "password123":
            signin_result.set("Sign-In Successful!")
        else:
            signin_result.set("Invalid credentials. Please try again.")


    @output
    @render.text
    def email_validity_flag():
        return "Valid email" if email_is_valid.get() else "Invalid email"
    @output
    @render.text
    def password_validity_flag():
        if not password_is_valid.get():
            return "❌ Passwords do not match"
        return "✅ Passwords match"
        
   ######################
    @output
    @render.ui
    def password_warning_text():
        password = input.signup_password()
        confirm_password = input.signup_password_confirm()
        if not passwords_match.get():
            return ui.p("❌ Passwords do not match", style="color: red")
        if len(password) < 8:
            return ui.p("Password needs to be at least 8 characters", style="color: grey")
        return ""

    @output
    @render.ui
    def email_warning_text():
        if not email_is_valid.get():
            return ui.p("❌ Invalid email address. Please format it like this JohnDoe@email.com", style="color: red")
        return ""

    @output
    @render.ui
    def name_error():
        return ui.p(signup_errors.get().get("name", ""), style="color: red")

    @output
    @render.ui
    def address_error():
        return ui.p(signup_errors.get().get("address", ""), style="color: red")

    @output
    @render.ui
    def employee_id_error():
        return ui.p(signup_errors.get().get("employee_id", ""), style="color: red")

    @output
    @render.ui
    def role_error():
        return ui.p(signup_errors.get().get("role", ""), style="color: red")

    @output
    @render.ui
    def retrieval_dropdown():
        choices = business_dropdown_choices.get()
        if not choices:
            return ui.p("No centers available.")
        return ui.input_select("retrieval_center", "Choose a Retrieval Center:", choices=choices)

    @output
    @render.text
    def retrieval_center_status():
        return f"Selected Center: {input.retrieval_center()}" if input.retrieval_center() else ""

    @reactive.Effect
    @reactive.event(input.save_signup_info)
    async def save_signup_info():
        email = input.signup_email()
        password = input.signup_password()
        confirm_password = input.signup_password_confirm()
        errors = {}

        if not input.signup_name().strip():
            errors["name"] = "❌ You need to have a valid Business Name"
        if not input.signup_address().strip():
            errors["address"] = "❌ You need to have a valid Business Address"
        if not input.signup_employee_id().strip():
            errors["employee_id"] = "❌ You need to have a valid Employee ID"
        if not input.signup_role().strip():
            errors["role"] = "❌ You need to select a Role"

        if not is_valid_email(email):
            email_is_valid.set(False)
            errors["email"] = "❌ You need to have a valid Email"
        else:
            email_is_valid.set(True)

        if not password or not confirm_password:
            errors["password"] = "❌ Password fields cannot be empty"
        elif password != confirm_password:
            errors["password"] = "❌ Passwords do not match"
            passwords_match.set(False)
        elif len(password) < 8:
            errors["password"] = "❌ Password must be at least 8 characters"
            password_is_valid.set(False)
        else:
            passwords_match.set(True)
            password_is_valid.set(True)

        if errors:
            signup_errors.set(errors)
            await session.send_custom_message("signup_save_status", {"value": ""})
            return

        signup_errors.set({})
        temp_signup_info.set({
            "name": input.signup_name(),
            "address": input.signup_address(),
            "email": email,
            "password": password,
            "confirm_password": confirm_password,
            "employee_id": input.signup_employee_id(),
            "role": input.signup_role()
        })
        session.send_input_message("signup_save_status", {"value": "✅ Info saved"})

    @reactive.Effect
    @reactive.event(input.final_register_btn)
    async def finalize_registration():
        if input.contract_agree():
            info = temp_signup_info.get()
            message = f"✅ {info['name']} at {info['address']} is registered successfully with SafeDrop."
            final_status_message.set(message)
            session.send_input_message("final_registration_status", {"value": message})
        else:
            message = "❌ Please agree to the contract to proceed."
            final_status_message.set(message)
            session.send_input_message("final_registration_status", {"value": message})
        

    @reactive.Effect
    @reactive.event(input.partner_signin_btn)
    def handle_partner_signin():
        email = input.partner_signin_email()
        password = input.partner_signin_password()
        info = temp_signup_info.get()

        # If nothing was registered, use the sample login
        if not info:
            if email == "sample@biz.com" and password == "sample123":
                partner_signin_status_val.set("✅ Sample login successful!")
                partner_signin_success_val.set(
                    "🎉 Welcome!\n"
                    "Business Name: Sample Market\n"
                    "Business Address: 123 Innovation Way\n"
                    "Employee ID: A1001\n"
                    "Role: CEO"
                )
            else:
                partner_signin_status_val.set("❌ Incorrect credentials.")
                partner_signin_success_val.set("")
            return

        # If business info *was* registered, match it
        if email == info.get("email") and password == info.get("password"):
            partner_signin_status_val.set("✅ Signed in successfully!")
            partner_signin_success_val.set(
                f"🎉 Welcome!\n"
                f"Business Name: {info['name']}\n"
                f"Business Address: {info['address']}\n"
                f"Employee ID: {info['employee_id']}\n"
                f"Role: {info['role']}"
            )
        else:
            partner_signin_status_val.set("❌ Incorrect credentials.")
            partner_signin_success_val.set("")

    # Initialize package data when the app loads
    initialize_mock_packages()

    @reactive.Effect
    @reactive.event(input.search_btn)
    def handle_search():
        query = input.search_query()
        results = search_package(query)
        session.send_input_message("search_results_data", {"value": results})

    @output
    @render.ui
    def search_results():
        query = input.search_query()
        if not query:
            return ui.p("No search input.")
        results = search_package(query)
        if not results:
            return ui.p("No matching packages found.")
        return ui.TagList(
            *[
                ui.card(
                    ui.h5(pkg["name"]),
                    ui.p(f"Tracking ID: {pkg['tracking_id']}"),
                    ui.p(f"Status: {pkg['status']}"),
                    ui.p(f"Size: {pkg['size']} | Weight: {pkg['weight']}"),
                    ui.p(f"Last Updated: {pkg['timestamp']}")
                )
                for pkg in results
            ]
        )
    
    def package_card(pkg, from_state, to_state, btn_id):
        tracking_id = pkg["tracking_id"]
        was_clicked = False

        if to_state == "ready_for_pickup":
            was_clicked = button_clicks_ready.get().get(tracking_id, False)
        elif to_state == "picked_up":
            was_clicked = button_clicks_picked.get().get(tracking_id, False)

        return ui.card(
            ui.h5(pkg["name"]),
            ui.p(f"Tracking ID: {tracking_id}"),
            ui.p(f"Size: {pkg['size']} | Weight: {pkg['weight']}"),
            ui.p(f"Last Updated: {pkg['timestamp']}"),
            ui.input_action_button(f"{btn_id}_{tracking_id}", f"Mark as {to_state.replace('_', ' ').title()}", class_="btn-outline-secondary"),
            ui.p(f"✅ Upon next system refresh, this will be moved to {to_state.replace('_', ' ').title()}.", style="color: green; font-weight: bold;") if was_clicked else ui.p("")
        )


    @output
    @render.ui
    def on_the_way_list():
        return ui.TagList(
            *[package_card(pkg, "on_the_way", "ready_for_pickup", "move_ready") for pkg in package_db["on_the_way"]]
        )

    @output
    @render.ui
    def ready_for_pickup_list():
        return ui.TagList(
            *[package_card(pkg, "ready_for_pickup", "picked_up", "move_picked") for pkg in package_db["ready_for_pickup"]]
        )

    @output
    @render.ui
    def picked_up_list():
        return ui.TagList(
            *[
                ui.card(
                    ui.h5(pkg["name"]),
                    ui.p(f"Tracking ID: {pkg['tracking_id']}"),
                    ui.p(f"Size: {pkg['size']} | Weight: {pkg['weight']}"),
                    ui.p(f"Picked Up: {pkg['timestamp']}")
                )
                for pkg in package_db["picked_up"]
            ]
        )

    @reactive.Effect
    @reactive.event(
        *[getattr(input, f"move_ready_{pkg['tracking_id']}") for pkg in package_db["on_the_way"]],
        *[getattr(input, f"move_picked_{pkg['tracking_id']}") for pkg in package_db["ready_for_pickup"]]
    )
    def fake_move_message():
        updated_ready = button_clicks_ready.get().copy()
        updated_picked = button_clicks_picked.get().copy()

        for pkg in package_db["on_the_way"]:
            btn_id = f"move_ready_{pkg['tracking_id']}"
            if getattr(input, btn_id, lambda: 0)() > 0:
                updated_ready[pkg['tracking_id']] = True

        for pkg in package_db["ready_for_pickup"]:
            btn_id = f"move_picked_{pkg['tracking_id']}"
            if getattr(input, btn_id, lambda: 0)() > 0:
                updated_picked[pkg['tracking_id']] = True

        button_clicks_ready.set(updated_ready)
        button_clicks_picked.set(updated_picked)


    @reactive.Effect
    @reactive.event(input.lock_center_btn)
    def lock_in_center():
        center = input.retrieval_center()
        if center:
            thank_you_msg.set(f"🎉 Thank you for using SafeDrop! Your package is set to be delivered at **{center}**.")

    @output
    @render.text
    def thank_you_message():
        return thank_you_msg.get()

    @output
    @render.text
    def signup_save_status():
        return "✅ Info saved" if temp_signup_info.get() else ""

    @output
    @render.text
    def final_registration_status():
        return final_status_message.get()
    
    @output
    @render.text
    def partner_signin_status():
        return partner_signin_status_val.get()

    @output
    @render.text
    def partner_signin_success_info():
        return partner_signin_success_val.get()

    @output
    @render.text
    def reminder_credentials():
        info = temp_signup_info.get()
        if info.get("email") and info.get("password"):
            return f"(Reminder) Your email: {info['email']} | Your password: {info['password']}"
        return ""
    @output
    @render.text
    def generated_code_display():
        return f"Generated Test Code: {generated_code.get()}" if generated_code.get() else ""

    @output
    @render.text
    def pickup_status():
        return pickup_result.get() if pickup_result.get() else ""

    @output
    @render.text
    def address_status():
        return f"✅ Address saved: {user_address.get()}" if user_address.get() else ""

    @output
    @render.image
    def display_logo():
        dir = Path(__file__).resolve().parent
        img: ImgData = {"src": str(dir / "safedrop_logo.png"), "width": "500px"}
        return img

    @output
    @render.ui
    def contract_text():
        return ui.HTML(get_fake_contract_text())

app = App(app_ui, server)
