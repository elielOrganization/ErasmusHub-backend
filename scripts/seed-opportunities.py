import sys
import os
from datetime import date

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlmodel import Session
from core.database import get_session
from models.opportunity import Opportunity
from schemas.opportunity_schema import OpportunityCreateTest

def seed_opportunities():

    opportunities_data = [
        {"name": "Erasmus+ Charles University - Computer Science", "city": "Praga", "desc": "Study at the oldest university in Central Europe."},
        {"name": "Masaryk University Exchange - Cyber Security", "city": "Brno", "desc": "Join the tech hub of the Czech Republic in Brno."},
        {"name": "Czech Technical University (CTU) - Engineering", "city": "Praga", "desc": "Top-tier technical education in the heart of Europe."},
        {"name": "University of West Bohemia - Applied Sciences", "city": "Pilsen", "desc": "Great engineering programs near the famous brewery."},
        {"name": "Palacký University - International Relations", "city": "Olomouc", "desc": "Study in a beautiful, historic student city."},
        {"name": "VŠB-TUO - Mining and Geology", "city": "Ostrava", "desc": "Industrial heritage meets modern research."},
        {"name": "University of Economics and Business (VŠE)", "city": "Praga", "desc": "Leading business school in the country."},
        {"name": "Brno University of Technology - Architecture", "city": "Brno", "desc": "Creative environment in the 'Czech Silicon Valley'."},
        {"name": "Mendel University - Forestry and Wood", "city": "Brno", "desc": "Research-focused programs in a green environment."},
        {"name": "Technical University of Liberec - Textile Design", "city": "Liberec", "desc": "Unique programs in Nanotechnology and Textiles."},
        {"name": "University of South Bohemia - Biology", "city": "České Budějovice", "desc": "Amazing nature and research facilities."},
        {"name": "University of Pardubice - Chemical Technology", "city": "Pardubice", "desc": "Specialized training in chemistry and transport."},
        {"name": "Tomas Bata University - Arts and Design", "city": "Zlín", "desc": "Modern campus with a focus on creative industries."},
        {"name": "Prague University of Creative Communication", "city": "Praga", "desc": "Focus on marketing, PR and creative writing."},
        {"name": "UCT Prague - Biotechnology", "city": "Praga", "desc": "Leading research in chemistry and life sciences."},
        {"name": "Jan Evangelista Purkyně University", "city": "Ústí nad Labem", "desc": "Environmental and social studies."},
        {"name": "University of Hradec Králové - Informatics", "city": "Hradec Králové", "desc": "Great student life and modern IT facilities."},
        {"name": "Czech University of Life Sciences (CZU)", "city": "Praga", "desc": "Environmental sciences and agriculture."},
        {"name": "AMU - Academy of Performing Arts", "city": "Praga", "desc": "Top-level education in film, music and drama."},
        {"name": "Silesian University in Opava - Physics", "city": "Opava", "desc": "Focused research and friendly atmosphere."},
        {"name": "University of Ostrava - Fine Arts", "city": "Ostrava", "desc": "Dynamic arts scene in an industrial city."},
        {"name": "Skoda Auto University - Logistics", "city": "Mladá Boleslav", "desc": "Unique connection with the automotive industry."},
        {"name": "Newton University - Management", "city": "Praga", "desc": "Focus on business leadership and management."},
        {"name": "CEVRO Institute - Political Science", "city": "Praga", "desc": "Specialized school for legal and political studies."},
        {"name": "Metropolitan University Prague - Anglophone Studies", "city": "Praga", "desc": "Internationally focused programs and community."},
    ]

    db_gen = get_session()
    db: Session = next(db_gen)

    try:
        for item in opportunities_data:
            data_test = OpportunityCreateTest(
                name=item["name"],
                description=item["desc"],
                country="Czech Republic",
                city=item["city"],
                status="open",
                start_date=date(2024, 9, 1),
                end_date=date(2025, 2, 15),
                creator_id=30
            )

            opp = Opportunity(**data_test.model_dump())
            db.add(opp)
        
        db.commit()
        print("Seed completado con éxito.")
    
    except Exception as e:
        print(f"Error durante el seed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_opportunities()