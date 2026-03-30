import json
from app import create_app
from app.extensions import db
from app.models.service import ServiceCategory, Service, PricingType

app = create_app()

DATA = """
{
  "services": [
    {
      "id": "business_office_printing",
      "name": "Business & Office Printing",
      "sub_services": [
        {"id": "business_cards", "name": "Business Cards", "price": 0.3},
        {"id": "letterheads", "name": "Letterheads", "price": 15},
        {"id": "envelopes_branded", "name": "Branded Envelopes", "price": 0.4},
        {"id": "brochures", "name": "Brochures", "price": null},
        {"id": "flyers", "name": "Flyers", "price": null},
        {"id": "posters", "name": "Posters", "price": null},
        {"id": "banners", "name": "Banners", "price": null}
      ]
    },
    {
      "id": "marketing_promotional",
      "name": "Marketing & Promotional Materials",
      "sub_services": [
        {"id": "stickers_labels", "name": "Stickers / Labels", "price": null},
        {"id": "catalogs", "name": "Catalogs", "price": null},
        {"id": "product_packaging", "name": "Product Packaging", "price": null},
        {"id": "gift_cards_vouchers", "name": "Gift Cards / Vouchers", "price": null},
        {"id": "menus", "name": "Menus", "price": null}
      ]
    },
    {
      "id": "large_format_display",
      "name": "Large Format & Display Items",
      "sub_services": [
        {"id": "banners_large", "name": "Banners", "price": null},
        {"id": "posters_large", "name": "Posters", "price": null},
        {"id": "signboards", "name": "Signboards", "price": null},
        {"id": "backdrops", "name": "Backdrops", "price": null},
        {"id": "car_branding", "name": "Car Branding Prints", "price": null}
      ]
    },
    {
      "id": "stationery_personal",
      "name": "Stationery & Personal Use",
      "sub_services": [
        {"id": "calendars", "name": "Calendars", "price": null},
        {"id": "wedding_invitations", "name": "Wedding Invitations", "price": null},
        {"id": "greeting_cards", "name": "Greeting Cards", "price": null},
        {"id": "certificates", "name": "Certificates", "price": null},
        {"id": "id_cards", "name": "ID Cards", "price": 6}
      ]
    },
    {
      "id": "packaging_industrial",
      "name": "Packaging & Industrial Printing",
      "sub_services": [
        {"id": "product_boxes", "name": "Product Boxes", "price": null},
        {"id": "paper_bags_branded", "name": "Branded Paper Bags", "price": null},
        {"id": "food_packaging_sleeves", "name": "Food Packaging Sleeves", "price": 1},
        {"id": "wrap_labels", "name": "Wrap-around Labels", "price": 1}
      ]
    }
  ]
}
"""

def seed_services():
    with app.app_context():
        data = json.loads(DATA)
        print("Starting to sync JSON structure into database...")
        
        for category_data in data.get('services', []):
            json_id = category_data['id']
            name = category_data['name']
            
            # Check if category exists by json_id, fallback to name for older records
            category = ServiceCategory.query.filter_by(json_id=json_id).first()
            if not category:
                category = ServiceCategory.query.filter_by(name=name).first()
                if category:
                    category.json_id = json_id
            
            if not category:
                category = ServiceCategory(
                    json_id=json_id,
                    name=name,
                    description=f"{name} provided by SAHAL Branding Agency.",
                    is_active=True
                )
                db.session.add(category)
                db.session.flush() # flush to get category.id
                print(f"Created category: {name}")
            else:
                category.name = name
                print(f"Updated category: {name}")

            for sub_data in category_data.get('sub_services', []):
                sub_id = sub_data['id']
                sub_name = sub_data['name']
                sub_price = sub_data['price']
                
                service = Service.query.filter_by(json_id=sub_id).first()
                if not service:
                    service = Service.query.filter_by(name=sub_name, category_id=category.id).first()
                    if service:
                        service.json_id = sub_id
                        
                if not service:
                    service = Service(
                        json_id=sub_id,
                        category_id=category.id,
                        name=sub_name,
                        description=f"{sub_name} under {name}.",
                        base_price=sub_price,
                        pricing_type=PricingType.fixed if sub_price is not None else PricingType.custom,
                        is_active=True
                    )
                    db.session.add(service)
                    print(f"Created service: {sub_name} (${sub_price})")
                else:
                    service.name = sub_name
                    service.base_price = sub_price
                    service.category_id = category.id
                    print(f"Updated service: {sub_name} (${sub_price})")

        db.session.commit()
        print("Successfully seeded services from JSON dataset.")

if __name__ == "__main__":
    seed_services()
