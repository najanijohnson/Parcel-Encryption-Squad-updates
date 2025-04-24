from shiny import App, ui, render, reactive  # Shiny for Python modules for UI creation, rendering, and reactivity
from utils import (                         # Importing utility functions and mock database from the utils module
    generate_test_pickup_code,              # Function to generate a fake pickup code for demo purposes
    validate_test_pickup_code,              # Function to check if entered pickup code matches the generated one
    get_local_businesses,                   # Function that returns a preset list of mock business names
    get_random_businesses_with_distances,   # Picks random businesses and attaches fake distances
    get_fake_contract_text,                 # Returns HTML-formatted fake contract for business registration
    is_valid_email,                         # Checks if an email format is valid
    package_db,                             # In-memory mock package database grouped by status
    move_package,                           # Moves a package from one state to another in the mock DB
    search_package,                         # Searches the mock DB for packages matching query
    initialize_mock_packages                # Pre-fills the mock DB with packages in various states
)
from shiny.types import ImgData             # For loading image assets in Shiny apps
from pathlib import Path                    # For referencing local files like images
import asyncio                              # Enables async functionality when needed

# UI layout definition
app_ui = ui.page_fluid(
    ui.output_image("display_logo", inline=True),  # Display the SafeDrop logo
    ui.br(),  # Line break for spacing
    ui.h2("From the Parcel Encryption Squad", style="font-family: 'Brush Script MT', cursive; font-size: 32px; font-weight: bold; color: #4B0082;"),  # Title with stylized font
    ui.p("A secure community-driven package pickup system.", style="font-family: 'Trebuchet MS', sans-serif; font-size: 16px; letter-spacing: 0.5px; color: #333;"),  # Tagline with styling

    # Role selection prompt
    ui.h4("Are you a Customer or Package Retrieval Partner?"),
    ui.input_action_button("role_customer", "Customer", class_="btn-info"),  # Button to choose customer role
    ui.input_action_button("role_partner", "Package Retrieval Partner", class_="btn-secondary"),  # Button to choose partner role
    ui.br(),  # Additional spacing

    ui.div(  # Hidden input field that tracks selected role
        ui.input_text("role_selected", label="0", value="0"),
        style="display: none"
    ),

    # Instructions / Landing Card (when no role is selected yet)
    ui.panel_conditional("input.role_selected == '0'",
        ui.card(
            ui.h3("📦 Welcome to Safe Drop!", style="color: #4a4a4a; font-weight: bold;"),  # Welcome header
            ui.p("Created with care by the Parcel Encryption Squad™", style="font-style: italic; color: #6c757d;"),  # Credit

            ui.p("This is a secure, community-powered system designed to keep your packages safe and your porch pirates unemployed.", 
                style="margin-top: 10px; font-size: 16px; line-height: 1.5;"),  # Mission statement

            ui.tags.ul(  # Instructions list
                ui.tags.li("👤 Are you a customer? Click the 'Customer' button to get a test pickup code and see nearby retrieval centers, no sign-in needed!", 
                        style="margin-bottom: 10px;"),
                ui.tags.li("🏪 Are you a package retrieval partner? Click 'Package Retrieval Partner' to register your business and manage deliveries like a boss.", 
                        style="margin-bottom: 10px;")
            ),

            ui.p("That’s it. No fluff. No fuss.", style="font-weight: 600; font-style: italic; margin-top: 15px;"),  # Humor tagline

            ui.p("💡 Fun fact: Najani, Meghan, and Kelvin didn’t just build a package system, they *engineered* the best pre-capstone project this side of campus. Sorry not sorry 🤷🏾‍♂️💅🏽",
                style="color: #198754; font-weight: bold; font-family: 'Comic Sans MS', cursive; font-size: 15px; margin-top: 20px;")  # Inside joke
        )
    ),

    # Customer section UI
    ui.panel_conditional("input.role_selected == 'customer'",
        ui.card(
            ui.h4("Test Customer Pickup"),  # Customer title
            ui.input_action_button("generate_code_btn", "Generate Test Pickup Code", class_="btn-warning"),  # Code generation button
            ui.output_text("generated_code_display"),  # Display the generated code
            ui.input_text("pickup_code", "Enter Your Pickup Code"),  # Input for the pickup code
            ui.input_action_button("pickup_btn", "Verify Pickup", class_="btn-success"),  # Verify button
            ui.output_text("pickup_status")  # Result message
        )
    ),

    # If pickup was successful, allow address entry
    ui.panel_conditional("output.pickup_status && output.pickup_status.includes('✅')",
        ui.card(
            ui.h4("Enter Your Address"),
            ui.input_text("user_address", "Your Address"),  # Input field for address
            ui.input_action_button("save_address_btn", "Find Nearby Package Retrieval", class_="btn-primary"),  # Trigger search
            ui.output_text("address_status")  # Result display
        )
    ),

    # If address is saved, show dropdown of nearby centers and confirm button
    ui.panel_conditional("output.address_status && output.address_status.includes('✅')",
        ui.card(
            ui.h4("Nearby Package Retrieval Centers"),
            ui.output_ui("retrieval_dropdown"),  # Dropdown populated with random businesses
            ui.output_text("retrieval_center_status"),  # Displays chosen center
            ui.input_action_button("lock_center_btn", "Lock In This Center", class_="btn-success"),  # Confirm button
            ui.output_text("thank_you_message")  # Thank-you message after confirmation
        )
    ),

    # Partner Section: Split into Register vs Sign In (distinction noted below)
    ui.panel_conditional("input.role_selected == 'partner'",
        ui.card(
            ui.input_radio_buttons("partner_action", "Choose an option:",
                choices=["Register a new business", "Sign in to existing business"]  # Two sub-options for partners
            )
        ),

        # Registration form shown when "Register a new business" is selected
        ui.panel_conditional("input.partner_action == 'Register a new business'",
            ui.card(
                ui.h4("Business Sign Up Form"),
                ui.input_text("signup_name", "Business Name"),  # Business name input
                ui.output_ui("name_error"),  # Inline validation message

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

        # Contract agreement card appears only if registration info is saved
        ui.panel_conditional("input.partner_action == 'Register a new business' && output.signup_save_status == '✅ Info saved'",
            ui.card(
                ui.h4("Agreements and Licensing"),
                ui.output_ui("contract_text"),  # Shows fake agreement text
                ui.input_checkbox("contract_agree", "I agree to the terms and conditions"),
                ui.input_action_button("final_register_btn", "Finalize Business Registration", class_="btn-success"),
                ui.output_text("final_registration_status")
            )
        ),

        # Sign-in form shown when "Sign in to existing business" is selected
        ui.panel_conditional("input.partner_action == 'Sign in to existing business'",
            ui.card(
                ui.h4("Sign In to Existing Business"),
                ui.output_text("reminder_credentials"),  # If user has already registered, remind them of their info
                ui.output_ui("sample_login_hint"),  # Show hint for using sample account (if no business was registered)
                ui.input_text("partner_signin_email", "Email"),
                ui.input_password("partner_signin_password", "Password"),
                ui.input_action_button("partner_signin_btn", "Sign In", class_="btn-success"),
                ui.output_text("partner_signin_status"),
                ui.output_text("partner_signin_success_info")
            )
        ),

        # Dashboard shown after successful sign-in
        ui.panel_conditional("input.partner_action == 'Sign in to existing business' && output.partner_signin_status.includes('✅')",
            ui.card(
                ui.h4("📦 Package Management Dashboard"),
                ui.input_text("search_query", "Search by name or tracking ID"),  # Search bar
                ui.input_action_button("search_btn", "Search", class_="btn-info"),  # Search button
                ui.output_ui("search_results")  # Render search results
            ),
            ui.card(
                ui.h4("🚚 Packages On the Way"),  # Lists packages marked as on the way
                ui.output_ui("on_the_way_list")
            ),
            ui.card(
                ui.h4("📍 Ready for Pickup"),  # Lists packages marked as ready
                ui.output_ui("ready_for_pickup_list")
            ),
            ui.card(
                ui.h4("✅ Picked Up in the Last 24 Hours"),  # Lists recently picked-up packages
                ui.output_ui("picked_up_list")
            )
        )
    )
)
#Server logic
def server(input, output, session):
    # Define reactive state variables to track inputs, outputs, and validation flags
    signin_result = reactive.Value("")                  # Result message for sign-in attempts
    passwords_match = reactive.Value(True)              # Tracks whether signup passwords match
    generated_code = reactive.Value("")                 # Stores the customer test pickup code
    pickup_result = reactive.Value("")                  # Result message after verifying pickup code
    user_address = reactive.Value("")                   # Stores the user's inputted delivery address
    business_dropdown_choices = reactive.Value([])      # List of businesses shown after address input
    temp_signup_info = reactive.Value({})               # Temporarily stores new business registration info
    email_is_valid = reactive.Value(True)               # Tracks if email input is valid
    password_is_valid = reactive.Value(True)            # Tracks if password input passes validation
    signup_errors = reactive.Value({})                  # Dictionary of form validation errors
    local_businesses = get_local_businesses()           # Loads list of available local business names
    final_status_message = reactive.Value("")           # Final status shown after business registration
    partner_signin_status_val = reactive.Value("")      # Tracks success/failure of sign-in
    partner_signin_success_val = reactive.Value("")     # Holds welcome message for signed-in business
    button_clicks_ready = reactive.Value({})            # Tracks button presses to mark packages as "ready"
    button_clicks_picked = reactive.Value({})           # Tracks button presses to mark packages as "picked up"
    thank_you_msg = reactive.Value("")                  # Message shown when customer locks in a center


    # When user selects "Customer", reset any old state and switch UI
    @reactive.Effect
    @reactive.event(input.role_customer)
    def _():
        generated_code.set("")
        pickup_result.set("")
        user_address.set("")
        business_dropdown_choices.set([])
        temp_signup_info.set({})
        session.send_input_message("role_selected", {"value": "customer"})

    # When user selects "Partner", reset customer state and switch UI
    @reactive.Effect
    @reactive.event(input.role_partner)
    def _():
        generated_code.set("")
        pickup_result.set("")
        user_address.set("")
        business_dropdown_choices.set([])
        temp_signup_info.set({})
        session.send_input_message("role_selected", {"value": "partner"})

    # Generate a random pickup code when button is clicked
    @reactive.Effect
    @reactive.event(input.generate_code_btn)
    def generate_test_code():
        code = generate_test_pickup_code()
        generated_code.set(code)

    # When user submits a pickup code, validate it
    @reactive.Effect
    @reactive.event(input.pickup_btn)
    def handle_pickup():
        entered_code = input.pickup_code().strip()  # Remove leading/trailing spaces
        if not entered_code:
            pickup_result.set("❌ Please enter your pickup code before verifying.")
            return
        
        # Check if entered code matches generated test code
        if validate_test_pickup_code(entered_code, generated_code.get()):
            pickup_result.set(f"✅ Pickup verified for code: {entered_code}")
        else:
            pickup_result.set("❌ **Sorry, that's not a valid pickup code. Please try again!**")

    # Save customer address and show nearby centers if address was entered
    @reactive.Effect
    @reactive.event(input.save_address_btn)
    def save_address():
        if input.role_selected() != "customer":
            return
        address = input.user_address()
        if address:
            user_address.set(address)
            # Randomly choose nearby centers and show them
            business_dropdown_choices.set(get_random_businesses_with_distances(local_businesses))
        else:
            business_dropdown_choices.set([])

    # Placeholder sign-in logic (used only for sample account testing)
    @reactive.Effect
    @reactive.event(input.signin_btn)
    def handle_signin():
        email = input.signup_email().strip().lower()
        password = input.signin_password()
        
        # Sample account hardcoded logic
        if email == "test@email.com" and password == "password123":
            signin_result.set("Sign-In Successful!")
        else:
            signin_result.set("Invalid credentials. Please try again.")

    # Flag that returns whether the entered email is valid
    @output
    @render.text
    def email_validity_flag():
        return "Valid email" if email_is_valid.get() else "Invalid email"

    # Flag that returns whether signup passwords matched
    @output
    @render.text
    def password_validity_flag():
        if not password_is_valid.get():
            return "❌ Passwords do not match"
        return "✅ Passwords match"

    # Display a password warning or guidance text during signup
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

    # Display a warning if the email is not formatted correctly
    @output
    @render.ui
    def email_warning_text():
        if not email_is_valid.get():
            return ui.p("❌ Invalid email address. Please format it like this JohnDoe@email.com", style="color: red")
        return ""

    # Inline error messages for registration form fields
    @output
    @render.ui
    def name_error():
        return ui.p(signup_errors.get().get("name", ""), style="color: red")
    
    # Displays error if the business address field is invalid during registration
    @output
    @render.ui
    def address_error():
        return ui.p(signup_errors.get().get("address", ""), style="color: red")

    # Displays error if the employee ID is invalid or missing during registration
    @output
    @render.ui
    def employee_id_error():
        return ui.p(signup_errors.get().get("employee_id", ""), style="color: red")

    # Displays error if the user doesn’t select a role during business signup
    @output
    @render.ui
    def role_error():
        return ui.p(signup_errors.get().get("role", ""), style="color: red")

    # Dynamically generates the dropdown of available pickup centers based on address
    @output
    @render.ui
    def retrieval_dropdown():
        choices = business_dropdown_choices.get()
        if not choices:
            return ui.p("No centers available.")  # Show message if none are found
        return ui.input_select("retrieval_center", "Choose a Retrieval Center:", choices=choices)

    # Shows which center was selected from the dropdown menu
    @output
    @render.text
    def retrieval_center_status():
        return f"Selected Center: {input.retrieval_center()}" if input.retrieval_center() else ""

    # Handles validation and saving of new business registration info
    @reactive.Effect
    @reactive.event(input.save_signup_info)
    async def save_signup_info():
        # Get and clean email/passwords
        email = input.signup_email().strip().lower()
        password = input.signup_password()
        confirm_password = input.signup_password_confirm()
        errors = {}

        # Validate all required fields
        if not input.signup_name().strip():
            errors["name"] = "❌ You need to have a valid Business Name"
        if not input.signup_address().strip():
            errors["address"] = "❌ You need to have a valid Business Address"
        if not input.signup_employee_id().strip():
            errors["employee_id"] = "❌ You need to have a valid Employee ID"
        if not input.signup_role().strip():
            errors["role"] = "❌ You need to select a Role"

        # Validate email format
        if not is_valid_email(email):
            email_is_valid.set(False)
            errors["email"] = "❌ You need to have a valid Email"
        else:
            email_is_valid.set(True)

        # Validate passwords
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

        # If any errors exist, stop here and show them
        if errors:
            signup_errors.set(errors)
            await session.send_custom_message("signup_save_status", {"value": ""})
            return

        # Save the valid registration data
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

        # Show confirmation message
        session.send_input_message("signup_save_status", {"value": "✅ Info saved"})

    # Confirms registration after user agrees to the contract terms
    @reactive.Effect
    @reactive.event(input.final_register_btn)
    async def finalize_registration():
        if input.contract_agree():
            info = temp_signup_info.get()
            message = f"✅ {info['name']} at {info['address']} is registered successfully with SafeDrop."
            final_status_message.set(message)
            session.send_input_message("final_registration_status", {"value": message})
        else:
            # Reject if they didn’t check the agreement box
            message = "❌ Please agree to the contract to proceed."
            final_status_message.set(message)
            session.send_input_message("final_registration_status", {"value": message})

    # Resets sign-in feedback (clears previous login messages) when switching modes
    @reactive.Effect
    @reactive.event(input.partner_action)
    def reset_signin_data():
        partner_signin_success_val.set("")
        partner_signin_status_val.set("")

    # Handles login logic for business users (either sample or user-created)
    @reactive.Effect
    @reactive.event(input.partner_signin_btn)
    def handle_partner_signin():
        # Reset any previous login feedback
        partner_signin_success_val.set("")
        partner_signin_status_val.set("")

        # Clean up user input
        email = input.partner_signin_email().strip().lower()
        password = input.partner_signin_password()

        info = temp_signup_info.get()  # Load stored business info if available

        # If nothing was registered, assume sample account usage
        if not info:
            email = email.strip().lower()
            password = password.strip()  # Slightly forgiving for demo use

        # Match sample login if no info was stored
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

        # Match real registered business login
        if email == info.get("email").strip().lower() and password == info.get("password").strip():
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

    # Populate the package database with mock data when the app first launches
    initialize_mock_packages()

    # Define what happens when the "Search" button is clicked
    @reactive.Effect
    @reactive.event(input.search_btn)
    def handle_search():
        query = input.search_query()  # Get the search term entered by the user
        results = search_package(query)  # Look for matches in the mock package DB
        session.send_input_message("search_results_data", {"value": results})  # Send results to UI

    # Render the search results in the UI
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

    # Reusable function to generate a UI card for a package
    def package_card(pkg, from_state, to_state, btn_id):
        tracking_id = pkg["tracking_id"]
        was_clicked = False  # Check if button was clicked to show feedback

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

    # Display packages currently on the way
    @output
    @render.ui
    def on_the_way_list():
        return ui.TagList(
            *[package_card(pkg, "on_the_way", "ready_for_pickup", "move_ready") for pkg in package_db["on_the_way"]]
        )

    # Display packages that are ready to be picked up
    @output
    @render.ui
    def ready_for_pickup_list():
        return ui.TagList(
            *[package_card(pkg, "ready_for_pickup", "picked_up", "move_picked") for pkg in package_db["ready_for_pickup"]]
        )

    # Display packages that were picked up in the last 24 hours
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

    # Logic to simulate moving a package between states using a button click
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

    # Conditional UI hint for using the sample login
    @output
    @render.ui
    def sample_login_hint():
        if not temp_signup_info.get():
            return ui.p("(You can use the sample login — Email: sample@biz.com | Password: sample123)", style="color: gray; font-style: italic;")
        return ""

    # Set the thank-you message once a retrieval center is locked in
    @reactive.Effect
    @reactive.event(input.lock_center_btn)
    def lock_in_center():
        center = input.retrieval_center()
        if center:
            thank_you_msg.set(f"🎉 Thank you for using SafeDrop! Your package is set to be delivered at **{center}**.")

    # Display the thank-you message in the UI
    @output
    @render.text
    def thank_you_message():
        return thank_you_msg.get()

    # Display sign-up status message after submitting business info
    @output
    @render.text
    def signup_save_status():
        return "✅ Info saved" if temp_signup_info.get() else ""

    # Display message after registration is finalized
    @output
    @render.text
    def final_registration_status():
        return final_status_message.get()

    # Show login result for partner
    @output
    @render.text
    def partner_signin_status():
        return partner_signin_status_val.get()

    # Show partner info after successful login
    @output
    @render.text
    def partner_signin_success_info():
        return partner_signin_success_val.get()

    # Display a reminder of credentials after registration
    @output
    @render.text
    def reminder_credentials():
        info = temp_signup_info.get()
        if info.get("email") and info.get("password"):
            return f"(Reminder) Your email: {info['email']} | Your password: {info['password']}"
        return ""

    # Display the generated test pickup code
    @output
    @render.text
    def generated_code_display():
        return f"Generated Test Code: {generated_code.get()}" if generated_code.get() else ""

    # Show the status of the pickup attempt
    @output
    @render.text
    def pickup_status():
        return pickup_result.get() if pickup_result.get() else ""

    # Show whether address entry was successful
    @output
    @render.text
    def address_status():
        return f"✅ Address saved: {user_address.get()}" if user_address.get() else ""

    # Render the logo image on the UI
    @output
    @render.image
    def display_logo():
        dir = Path(__file__).resolve().parent
        img: ImgData = {"src": str(dir / "safedrop_logo.png"), "width": "500px"}
        return img

    # Render the business contract text in HTML format
    @output
    @render.ui
    def contract_text():
        return ui.HTML(get_fake_contract_text())

# Link the UI and server to create the app
app = App(app_ui, server)
