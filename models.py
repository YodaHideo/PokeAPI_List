from app import db

class BattleHistory(db.Model):
    __tablename__ = 'battle_history'

    id = db.Column(db.Integer, primary_key=True)
    pokemon1_name = db.Column(db.String(50), nullable=False)
    pokemon2_name = db.Column(db.String(50), nullable=False)
    round_data = db.Column(db.JSON, nullable=False)

    def __init__(self, pokemon1_name, pokemon2_name, round_data):
        self.pokemon1_name = pokemon1_name
        self.pokemon2_name = pokemon2_name
        self.round_data = round_data
