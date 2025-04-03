from shiny import App, ui, render, reactive
from utils import register_business, notify_dropoff, verify_pickup
from shiny.types import ImgData
from pathlib import Path

app_ui = ui.page_fluid(
    {"id": "main-content"},
    ui.output_image("display_logo", inline=True),
    ui.br(),
    ui.h2("Parcel Encryption Squad"),
    ui.p("A secure community-driven package pickup system."),
    
    ui.card(
        ui.h4("Register a Business Location"),
        ui.input_text("business_name", "Business Name"),
        ui.input_text("business_address", "Address"),
        ui.input_action_button("register_btn", "Register Business", class_="btn-primary"),
        ui.output_text("registration_status")
    ),

    ui.card(
        ui.h4("Notify Drop-Off"),
        ui.input_text("tracking_number", "Package Tracking Number"),
        ui.input_text("business_code", "Business Location Code"),
        ui.input_text("recipient_name", "Recipient Name"),
        ui.input_action_button("dropoff_btn", "Notify Drop-Off", class_="btn-primary"),
        ui.output_text("dropoff_status")
    ),

    ui.card(
        ui.h4("Verify Pickup"),
        ui.input_text("pickup_code", "Pickup Verification Code"),
        ui.input_action_button("pickup_btn", "Verify Pickup", class_="btn-success"),
        ui.output_text("pickup_status")
    )
)

def server(input, output, session):
    @reactive.Effect
    @reactive.event(input.register_btn)
    def handle_register():
        name = input.business_name()
        address = input.business_address()
        status = register_business(name, address)
        ui.update_text("registration_status", status)

    @reactive.Effect
    @reactive.event(input.dropoff_btn)
    def handle_dropoff():
        tracking = input.tracking_number()
        code = input.business_code()
        recipient = input.recipient_name()
        status = notify_dropoff(tracking, code, recipient)
        ui.update_text("dropoff_status", status)

    @reactive.Effect
    @reactive.event(input.pickup_btn)
    def handle_pickup():
        code = input.pickup_code()
        status = verify_pickup(code)
        ui.update_text("pickup_status", status)


    @output
    @render.image
    def display_logo():
        dir = Path(__file__).resolve().parent
        img: ImgData = {"src": str(dir / "parcel-logo.jpg"), "width": "300px"}
        return img

app = App(app_ui, server)
