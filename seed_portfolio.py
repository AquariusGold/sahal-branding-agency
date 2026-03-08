from app import create_app
from app.extensions import db
from app.models.portfolio import PortfolioItem

app = create_app()

def seed_portfolio():
    with app.app_context():
        items = [
            {
                "title": "Eco-friendly Packaging Redesign",
                "client_name": "GreenLife Naturals",
                "category": "Branding",
                "description": "Complete brand overhaul and sustainable packaging design for a natural cosmetics line.",
                "image_url": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?q=80&w=600&auto=format&fit=crop",
                "is_active": True
            },
            {
                "title": "Tech Conference 2025",
                "client_name": "InnovateX",
                "category": "Event Production",
                "description": "Full-scale event production, LED stage design, and live streaming services for a 5000-attendee conference.",
                "image_url": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?q=80&w=600&auto=format&fit=crop",
                "is_active": True
            },
            {
                "title": "Modern Corporate Office Fit-out",
                "client_name": "FinTech HQ",
                "category": "Interior Design",
                "description": "Interior design and execution for a modern, open-plan office space featuring biophilic elements.",
                "image_url": "https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=600&auto=format&fit=crop",
                "is_active": True
            }
        ]

        if PortfolioItem.query.count() == 0:
            for item_data in items:
                portfolio_item = PortfolioItem(**item_data)
                db.session.add(portfolio_item)
            db.session.commit()
            print("Successfully seeded portfolio items.")
        else:
            print("Portfolio items already exist, skipping seed.")

if __name__ == "__main__":
    seed_portfolio()
