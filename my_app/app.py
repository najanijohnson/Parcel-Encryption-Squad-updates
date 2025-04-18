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
    is_valid_email
)
from shiny.types import ImgData
from pathlib import Path

#App UI ---
app_ui = ui.page_fluid(
    ui.output_image("display_logo", inline=True),
    ui.br(),
    ui.h2("Parcel Encryption Squad"),
    ui.p("A secure community-driven package pickup system."),

    ui.h4("Are you a Customer or Package Retrieval Partner?"),
    ui.input_action_button("role_customer", "Customer", class_="btn-info"),
    ui.input_action_button("role_partner", "Package Retrieval Partner", class_="btn-secondary"),
    ui.br(),

    ui.div(
        ui.input_text("role_selected", label="", value=""),
        style="display: none"
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
            ui.output_text("retrieval_center_status")
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
                ui.input_text("signup_address", "Business Address"),
                ui.input_text("signup_email", "Email"),
                ui.output_ui("email_warning_text"),
                ui.input_password("signup_password", "Password"),
                ui.input_password("signup_password_confirm", "Retype Password"),
                ui.output_ui("password_warning_text"),
                ui.input_text("signup_employee_id", "Employee ID"),
                ui.input_select("signup_role", "Your Role in the Company:",
                    choices=["CEO", "President", "Owner", "Manager", "Supervisor", "Other"]
                ),
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
                ui.h4("Notify Drop-Off"),
                ui.input_text("tracking_number", "Package Tracking Number"),
                ui.input_text("business_code", "Business Location Code"),
                ui.input_text("recipient_name", "Recipient Name"),
                ui.input_action_button("dropoff_btn", "Notify Drop-Off", class_="btn-primary"),
                ui.output_text("dropoff_status")
            )
        )
    )
)

# --- Server logic ---
def server(input, output, session):
    passwords_match = reactive.Value(True)
    generated_code = reactive.Value("")
    pickup_result = reactive.Value("")
    user_address = reactive.Value("")
    business_dropdown_choices = reactive.Value([])
    temp_signup_info = reactive.Value({})
    email_is_valid = reactive.Value(True)
    password_is_valid = reactive.Value(True)
    local_businesses = get_local_businesses()
    # gets rid of the error with the react call for the address being alled to 
    # package retrieval partner when swapped from customer to partner if saved 
    @reactive.Effect ################################################## for customer role
    @reactive.event(input.role_customer)
    def _():
        generated_code.set("") #this clears the fields so theres no overlap between roles
        pickup_result.set("")
        user_address.set("")
        business_dropdown_choices.set([])
        temp_signup_info.set({})
        
        session.send_input_message("role_selected", {"value": "customer"})

    @reactive.Effect ###################################################### for partner role
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
        if input.role_selected() != "customer": #should fix the error of seeing the address when not a customer
            return
        address = input.user_address()
        if address:
            user_address.set(address)
            business_dropdown_choices.set(get_random_businesses_with_distances(local_businesses))
        else:
            business_dropdown_choices.set([])
#########################
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

        # Check if passwords match
        if not passwords_match.get():
            return ui.p("❌ Passwords do not match", style="color: red")

        # Check if password is at least 8 characters long
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
        confirm = input.signup_password_confirm()
        #checking validity
        if not is_valid_email(email):
            email_is_valid.set(False)
            #email = input.signup_email() #this causes crashes! DONT UNCOMMENT
            await session.send_custom_message("signup_save_status", {"value": "❌ Invalid email address"})
            return
        email_is_valid.set(True)
        
        if password != confirm:
            passwords_match.set(False)
            await session.send_custom_message("signup_save_status", {"value": "❌ Passwords do not match"})
            return
        passwords_match.set(True)   
        
        if len(password) < 8:
            password_is_valid.set(False)
            await session.send_custom_message("signup_save_status", {"value": "❌ Password needs to be at least 8 characters"})
            return
        password_is_valid.set(True)
        # Save the signup information to a temporary storage
        temp_signup_info.set({
            "name": input.signup_name(),
            "address": input.signup_address(),
            "email": email,
            "password": password,
            "confirm_password": confirm,
            "employee_id": input.signup_employee_id(),
            "role": input.signup_role()
        })
        await session.send_custom_message("signup_save_status", {"value": "✅ Info saved"})

    @reactive.Effect
    @reactive.event(input.final_register_btn)
    def finalize_registration():
        if input.contract_agree():
            info = temp_signup_info.get()
            session.send_custom_message("final_registration_status", {
                "value": f"✅ Business '{info['name']}' at '{info['address']}' registered."
            })
        else:
            session.send_custom_message("final_registration_status", {
                "value": "❌ Please agree to the contract to proceed."
            })

    @output
    @render.text
    def signup_save_status():
        return "✅ Info saved" if temp_signup_info.get() else ""

    @output
    @render.text
    def final_registration_status():
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
