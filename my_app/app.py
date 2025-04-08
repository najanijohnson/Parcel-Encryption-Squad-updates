from shiny import App, ui, render, reactive
from utils import (
    register_business,
    notify_dropoff,
    verify_pickup,
    generate_test_pickup_code,
    validate_test_pickup_code
)
from shiny.types import ImgData
from pathlib import Path

# --- App UI ---
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
  # Hidden role selector

    # Customer section
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

    # Partner section
    ui.panel_conditional("input.role_selected == 'partner'",
        ui.card(
            ui.input_radio_buttons("partner_action", "Choose an option:",
                choices=["Register a new business", "Sign in to existing business"]
            )
        ),

        ui.panel_conditional("input.partner_action == 'Register a new business'",
            ui.card(
                ui.h4("Register a Business Location"),
                ui.input_text("business_name", "Business Name"),
                ui.input_text("business_address", "Address"),
                ui.input_action_button("register_btn", "Register Business", class_="btn-primary"),
                ui.output_text("registration_status")
            )
        ),

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
    generated_code = reactive.Value("")
    pickup_result = reactive.Value("")

    @reactive.Effect
    @reactive.event(input.role_customer)
    def _():
        session.send_input_message("role_selected", {"value": "customer"})

    @reactive.Effect
    @reactive.event(input.role_partner)
    def _():
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
    @reactive.event(input.register_btn)
    def handle_register():
        name = input.business_name()
        address = input.business_address()
        status = register_business(name, address)
        session.send_custom_message("registration_status", {"value": status})

    # When the drop-off button is clicked, call the drop-off notification logic
    @reactive.Effect
    @reactive.event(input.dropoff_btn)
    def handle_dropoff():
        tracking = input.tracking_number()
        code = input.business_code()
        recipient = input.recipient_name()
        status = notify_dropoff(tracking, code, recipient)
        session.send_custom_message("dropoff_status", {"value": status})

    @output
    @render.text
    def generated_code_display():
        return f"Generated Test Code: {generated_code.get()}" if generated_code.get() else ""

    @output
    @render.text
    def pickup_status():
        return pickup_result.get()

    @output
    @render.image
    def display_logo():
        dir = Path(__file__).resolve().parent
        img: ImgData = {"src": str(dir / "parcel-logo.jpg"), "width": "300px"}
        return img

app = App(app_ui, server)
