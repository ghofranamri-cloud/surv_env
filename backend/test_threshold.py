import unittest
from threshold_engine import analyser, generer_alertes

class TestThresholdEngine(unittest.TestCase):
    def test_evaluer_capteur_low(self):
        result = analyser(20.0, 50.0, 100, 100, 100)
        self.assertEqual(result["priorite"], "LOW")
        self.assertEqual(result["etats"], {
            "temperature": "LOW",
            "humidite": "LOW",
            "fumee": "LOW",
            "poussiere": "LOW",
            "son": "LOW"
        })

    def test_priorite_high_and_alertes(self):
        result = analyser(36.0, 65.0, 250, 350, 500)
        self.assertEqual(result["priorite"], "HIGH")
        self.assertEqual(result["etats"]["temperature"], "HIGH")
        alertes = generer_alertes(result["etats"])
        self.assertTrue(any(a["capteur"] == "temperature" and a["niveau"] == "HIGH" for a in alertes))

    def test_critical_alert(self):
        result = analyser(45.0, 85.0, 450, 650, 750)
        self.assertEqual(result["priorite"], "CRITICAL")
        alertes = generer_alertes(result["etats"])
        self.assertTrue(any(a["niveau"] == "CRITICAL" for a in alertes))

    def test_generer_alertes_low_returns_empty(self):
        self.assertEqual(generer_alertes({
            "temperature": "LOW",
            "humidite": "LOW",
            "fumee": "LOW",
            "poussiere": "LOW",
            "son": "LOW"
        }), [])

if __name__ == "__main__":
    unittest.main()
