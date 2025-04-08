from shiny import App, ui, render, reactive
from utils import register_business, notify_dropoff, verify_pickup
from shiny.types import ImgData
from pathlib import Path

# Running locally (for MH) using: python -m shiny run --reload app.py 
# This is required due to how Shiny needs to be invoked in this environment.

# Shared styling for centering and constraining content width
centered_div_style = {
    "style": "margin: 10px auto; width: 50%; text-align: center;"
}

app_ui = ui.page_fluid(
    {"id": "main-content"},

    # Display the logo image at the top of the page, centered
    ui.div(
        {"style": "text-align: center; margin-top: 20px;"},
        ui.output_image("display_logo", inline=True)
    ),

    ui.br(),

    # Title and introductory paragraph, also centered
    ui.div(
        {"style": "text-align: center;"},
        ui.h2("Parcel Encryption Squad"),
        ui.p("A secure community-driven package pickup system.")
    ),

    # Section: Register a Business Location
    ui.div(centered_div_style,
        ui.card(
            ui.h4("Register a Business Location"),
            ui.input_text("business_name", "Business Name"),
            ui.input_text("business_address", "Address"),
            ui.input_action_button("register_btn", "Register Business", class_="btn-primary"),
            ui.output_text("registration_status")
        )
    ),

    # Section: Notify Drop-Off
    ui.div(centered_div_style,
        ui.card(
            ui.h4("Notify Drop-Off"),
            ui.input_text("tracking_number", "Package Tracking Number"),
            ui.input_text("business_code", "Business Location Code"),
            ui.input_text("recipient_name", "Recipient Name"),
            ui.input_action_button("dropoff_btn", "Notify Drop-Off", class_="btn-primary"),
            ui.output_text("dropoff_status")
        )
    ),

    # Section: Verify Pickup
    ui.div(centered_div_style,
        ui.card(
            ui.h4("Verify Pickup"),
            ui.input_text("pickup_code", "Pickup Verification Code"),
            ui.input_action_button("pickup_btn", "Verify Pickup", class_="btn-success"),
            ui.output_text("pickup_status")
        )
    )
)

def server(input, output, session):
    # When the register button is clicked, call the registration logic
    @reactive.Effect
    @reactive.event(input.register_btn)
    def handle_register():
        name = input.business_name()
        address = input.business_address()
        status = register_business(name, address)
        ui.update_text("registration_status", status)

    # When the drop-off button is clicked, call the drop-off notification logic
    @reactive.Effect
    @reactive.event(input.dropoff_btn)
    def handle_dropoff():
        tracking = input.tracking_number()
        code = input.business_code()
        recipient = input.recipient_name()
        status = notify_dropoff(tracking, code, recipient)
        ui.update_text("dropoff_status", status)

    # When the pickup button is clicked, call the pickup verification logic
    @reactive.Effect
    @reactive.event(input.pickup_btn)
    def handle_pickup():
        code = input.pickup_code()
        status = verify_pickup(code)
        ui.update_text("pickup_status", status)

    # Load and display the logo image from the project directory
    @output
    @render.image
    def display_logo():
        dir = Path(__file__).resolve().parent
        img: ImgData = {"src": str(dir / "parcel-logo.jpg"), "width": "300px"}
        return img

app = App(app_ui, server)
