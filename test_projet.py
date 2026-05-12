import json
from projet import add_day_to_history, is_first_launch, get_greeting



def test_get_greeting():
    for i in range(12):
        assert get_greeting(i) == "Bonjour"
    for i in range(12, 18):
        assert get_greeting(i) == "Bon après-midi"
    for i in range(18,24):
        assert get_greeting(i) == "Bonsoir"
    # Test avec une autre langue
    assert get_greeting(8, "en") == "Good morning"
    assert get_greeting(14, "en") == "Good afternoon"
    assert get_greeting(20, "en") == "Good evening"
    
def test_is_first_launch(monkeypatch, tmp_path):
    # tmp_path = dossier temporaire créé par pytest, supprimé après le test

    # Cas 1 : fichier absent,  premier lancement
    fake_path = tmp_path / "profile.json"
    monkeypatch.setattr("projet.PROFILE_FILE", fake_path)
    assert is_first_launch() == True

    # Cas 2 : fichier présent, pas premier lancement
    fake_path.write_text("{}")  # crée le fichier
    assert is_first_launch() == False
    
    
def test_add_day_to_history(monkeypatch, tmp_path):
    # Crée un profil JSON minimal dans un dossier temporaire
    fake_path = tmp_path / "profile.json"
    fake_path.write_text(json.dumps({"history": []}))

    monkeypatch.setattr("projet.PROFILE_FILE", fake_path)

    program = {"score": 8, "slots": [], "quote": "Test"}
    weather = {"city": "Oyem", "condition": "clear", "temp": 22}

    result = add_day_to_history(program, weather)

    # Vérifie que la fonction retourne True
    assert result == True

    # Vérifie que l'entrée a bien été ajoutée
    data = json.loads(fake_path.read_text())
    assert len(data["history"]) == 1
    assert data["history"][0]["city"] == "Oyem"
    assert data["history"][0]["score"] == 8