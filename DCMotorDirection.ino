/* Code for the Nerf's reloading mechanism and firing mechanism */

#define IN1 2
#define IN2 3
#define EN 4
#define SENSE A0
#define LOADED 8
#define TRIGGER 7
#define PUSHBUTTON 12
// Values for the current to voltage (ADC input)
#define fwdStop 550 // Reloading value
#define revStop 70  // Snap back value

int loadedGun = false;
int shoot = LOW;

struct Sentry {
  bool loaded = true; // Press trigger to reload first time
  int bullets = 7;

  bool isGunLoaded () {
    if (loaded) {
      digitalWrite(LOADED, HIGH);
      return true;
    }
    else {
      digitalWrite(LOADED, LOW);
      return false;
    }
  }

  void shootTarget() {
    if (loaded) {
      digitalWrite(TRIGGER, HIGH);
      delay(50);
      digitalWrite(TRIGGER, LOW);
      loaded = false;
      bullets--;
      isGunLoaded();
    }
  }

  void reloadGun() {
    if ((!loaded) && (bullets > 0)) {
      int sencurrA = 0;
      int sencurrB = 0;
      fwdDirection();
      startMotor();
      shortPause();
      while (sencurrA < fwdStop) {
        sencurrA = analogRead(SENSE);
        Serial.print("Reloading: ");
        Serial.println(sencurrA);
      }
      loaded = true;
      isGunLoaded();
      sencurrA = 0; // Reset sensor value

      revDirection();
      shortPause();
      while (sencurrB < revStop) {
        sencurrB = analogRead(SENSE);
        Serial.print("Snapping back: ");
        Serial.println(sencurrB);
      }
      sencurrB = 0; // Reset sensor value
      stopMotor();
    }
  }

  void fwdDirection() {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
  }

  void revDirection() {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
  }

  void startMotor() {
    digitalWrite(EN, HIGH);
  }

  void stopMotor() {
    digitalWrite(EN, LOW);
  }

  void shortPause() {
    delay(300);
  }
} turret;

void setup() {
  Serial.begin(9600);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(EN, OUTPUT);
  pinMode(LOADED, OUTPUT);
  pinMode(TRIGGER, OUTPUT);
  pinMode(PUSHBUTTON, INPUT);
}

void loop() {
  digitalWrite(EN, LOW);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  Serial.println("Starting...");
  delay(1000);

  while (1) {
    loadedGun = turret.isGunLoaded();
    if (!loadedGun)
      turret.reloadGun();
      
    loadedGun = turret.isGunLoaded();
    shoot = digitalRead(PUSHBUTTON);
    if (loadedGun && (shoot == HIGH))
      turret.shootTarget();
  }
}
