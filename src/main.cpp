#include <Arduino.h>
#include <DHT.h>
#include <LiquidCrystal_I2C.h>
#include <Adafruit_NeoPixel.h>


// PINS

#define DHT_PIN      2
#define DHT_TYPE     DHT22
#define MQ2_PIN      A0
#define POUS_PIN     A1
#define SON_PIN      A2
#define STRIP_PIN    5
#define BUZZER_PIN   9


// SEUILS

#define SEUIL_TEMP      40.0   // °C
#define SEUIL_HUM       80.0   // %
#define SEUIL_FUMEE     400    // valeur analogique
#define SEUIL_POUS      600    // valeur analogique
#define SEUIL_SON       700    // valeur analogique (~85 dB)

// Seuils warning (80% du seuil critique)
#define WARN_TEMP       (SEUIL_TEMP  * 0.85)
#define WARN_HUM        (SEUIL_HUM   * 0.85)
#define WARN_FUMEE      (SEUIL_FUMEE * 0.75)
#define WARN_POUS       (SEUIL_POUS  * 0.75)
#define WARN_SON        (SEUIL_SON   * 0.80)


// OBJETS

DHT               dht(DHT_PIN, DHT_TYPE);
LiquidCrystal_I2C lcd(0x27, 16, 2);
Adafruit_NeoPixel strip(5, STRIP_PIN, NEO_GRB + NEO_KHZ800);


// COULEURS LED STRIP

uint32_t VERT   ;
uint32_t JAUNE  ;
uint32_t ROUGE  ;
uint32_t ETEINT ;


// VARIABLES GLOBALES

int   page             = 0;
unsigned long dernierChangementPage = 0;
unsigned long dernierEnvoi          = 0;


// FONCTIONS UTILITAIRES


void bip(int nb, int duree) {
  for (int i = 0; i < nb; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(duree);
    digitalWrite(BUZZER_PIN, LOW);
    delay(100);
  }
}

// Retourne la couleur selon valeur et seuils
uint32_t couleurCapteur(float valeur, float seuil, float warn) {
  if (valeur >= seuil) return ROUGE;
  if (valeur >= warn)  return JAUNE;
  return VERT;
}

// Met à jour le strip : 1 LED par capteur
void majStrip(float temp, float hum, int fumee, int pous, int son) {
  strip.setPixelColor(0, couleurCapteur(temp,  SEUIL_TEMP,  WARN_TEMP));
  strip.setPixelColor(1, couleurCapteur(hum,   SEUIL_HUM,   WARN_HUM));
  strip.setPixelColor(2, couleurCapteur(fumee, SEUIL_FUMEE, WARN_FUMEE));
  strip.setPixelColor(3, couleurCapteur(pous,  SEUIL_POUS,  WARN_POUS));
  strip.setPixelColor(4, couleurCapteur(son,   SEUIL_SON,   WARN_SON));
  strip.show();
}

// Affiche une page sur le LCD
void afficherPage(int p, float temp, float hum, int fumee, int pous, int son, bool alerte) {
  lcd.clear();
  switch (p) {

    case 0:
      lcd.setCursor(0, 0);
      lcd.print("T:");
      lcd.print(temp, 1);
      lcd.print("C H:");
      lcd.print((int)hum);
      lcd.print("%");
      lcd.setCursor(0, 1);
      lcd.print(alerte ? ">>> ALERTE <<<  " : "   Etat: OK     ");
      break;

    case 1:
      lcd.setCursor(0, 0);
      lcd.print("Fumee:  ");
      lcd.print(fumee);
      lcd.setCursor(0, 1);
      lcd.print("Pous:   ");
      lcd.print(pous);
      break;

    case 2:
      lcd.setCursor(0, 0);
      lcd.print("Son:    ");
      lcd.print(son);
      lcd.setCursor(0, 1);
      lcd.print(son > SEUIL_SON ? "Bruit excessif! " : "Son: Normal     ");
      break;
  }
}

// Envoie les données vers Python via Serial (format JSON)
void envoyerDonnees(float temp, float hum, int fumee, int pous, int son, bool alerte) {
  Serial.print("{");
  Serial.print("\"temperature\":");
  Serial.print(temp, 1);
  Serial.print(",\"humidite\":");
  Serial.print(hum, 1);
  Serial.print(",\"fumee\":");
  Serial.print(fumee);
  Serial.print(",\"poussiere\":");
  Serial.print(pous);
  Serial.print(",\"son\":");
  Serial.print(son);
  Serial.print(",\"alerte\":");
  Serial.print(alerte ? "true" : "false");
  Serial.println("}");
}


// SETUP

void setup() {
  Serial.begin(9600);

  // Initialisation couleurs (après begin)
  strip.begin();
  strip.show();
  VERT   = strip.Color(0,   255, 0);
  JAUNE  = strip.Color(255, 180, 0);
  ROUGE  = strip.Color(255, 0,   0);
  ETEINT = strip.Color(0,   0,   0);

  dht.begin();

  lcd.init();
  lcd.backlight();

  pinMode(BUZZER_PIN, OUTPUT);

  // Message de démarrage
  lcd.setCursor(0, 0);
  lcd.print(" Surveillance  ");
  lcd.setCursor(0, 1);
  lcd.print(" Yura Corp.    ");
  delay(2000);
  lcd.clear();
}


// LOOP

void loop() {
  unsigned long maintenant = millis();

  // === Lecture capteurs ===
  float temp  = dht.readTemperature();
  float hum   = dht.readHumidity();
  int   fumee = analogRead(MQ2_PIN);
  int   pous  = analogRead(POUS_PIN);
  int   son   = analogRead(SON_PIN);

  // === Vérification DHT22 ===
  if (isnan(temp) || isnan(hum)) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Erreur DHT22 !");
    delay(2000);
    return;
  }

  // === Déterminer niveau d'alerte ===
  bool alerte = (
    temp  >= SEUIL_TEMP  ||
    hum   >= SEUIL_HUM   ||
    fumee >= SEUIL_FUMEE ||
    pous  >= SEUIL_POUS  ||
    son   >= SEUIL_SON
  );

  bool warning = (
    temp  >= WARN_TEMP  ||
    hum   >= WARN_HUM   ||
    fumee >= WARN_FUMEE ||
    pous  >= WARN_POUS  ||
    son   >= WARN_SON
  );

  // === Mise à jour LED strip ===
  majStrip(temp, hum, fumee, pous, son);

  // === Buzzer ===
  if (alerte)       bip(2, 300);
  else if (warning) bip(1, 100);

  // === Rotation page LCD toutes les 3 secondes ===
  if (maintenant - dernierChangementPage >= 3000) {
    page = (page + 1) % 3;
    dernierChangementPage = maintenant;
    afficherPage(page, temp, hum, fumee, pous, son, alerte);
  }

  // === Envoi série toutes les 2 secondes ===
  if (maintenant - dernierEnvoi >= 2000) {
    envoyerDonnees(temp, hum, fumee, pous, son, alerte);
    dernierEnvoi = maintenant;
  }

  delay(100);
}
