/*
  @file Motor driver DRI0042_Test.ino
  @brief DRI0042_Test.ino  Motor control program

  control motor positive inversion

  @author bernie.chen@dfrobot.com
  @version  V1.0
  @date  2016-8-10
*/
const int IN1 = 5; //yellow
const int IN2 = 4; //orange
const int ENA = 6; //blue

const int IN3 = 8; //white
const int IN4 = 7; //green
const int ENB = 9; //purple

const char* directions[2] = {"Forward", "Reverse"};

const int ledPin = 13;      // select the pin for the LED


int motor1_dir = 0;
int motor2_dir = 0;
int motor1_speed = 0;
int motor2_speed = 0;

void establishContact() {
  while (Serial.available() <= 0) {
    //Serial.print('A');   // send a capital A
    delay(100);
  }
}

void status(int motor) {
  int spd;
  char* dir; 
  int dir_value;
  if (motor == 1) {
    dir = directions[motor1_dir];
    dir_value = motor1_dir;
    spd = motor1_speed; 
  } else {
    dir = directions[motor2_dir];
    dir_value = motor2_dir;
    spd = motor2_speed; 
  }
  Serial.print("Motor #");
  Serial.print(motor);
  Serial.print(" Direction: ");
  Serial.print(dir);
  Serial.print("("); 
  Serial.print(dir_value);
  Serial.print(") ");
  Serial.print(" Speed: ");
  if (spd) {
    Serial.print(spd);
  } else {
    Serial.print("Stopped");
  }
  Serial.print("\n");
  
}

void short_status(int motor) {
  int spd;
  char dir; 
  int dir_value;
  if (motor == 1) {
    dir = directions[motor1_dir][0];
    dir_value = motor1_dir;
    spd = motor1_speed; 
  } else {
    dir = directions[motor2_dir][0];
    dir_value = motor2_dir;
    spd = motor2_speed; 
  }
  Serial.print(motor);
  Serial.print(dir);
  Serial.print(spd);
  Serial.print('\n');
  
}

void adjust(int motor, int amt) {
  if (motor == 1) {
    amt = motor1_dir? amt: -1*amt;
    motor1_speed += amt;
    if (motor1_speed < 0) {
      motor1_speed *= -1;
      motor1_dir = motor1_dir ? 0 : 1;
    }
  }

  else {
    amt = motor2_dir? amt: -1*amt;
    motor2_speed += amt;
    if (motor2_speed < 0) {
      motor2_speed *= -1;
      motor2_dir = motor2_dir ? 0 : 1;
    }
  }
}

char sernext() {
  while (true) {
    if (!Serial.available() > 0) continue;
    return Serial.read();
  }
}

void handleSerial() {
  char target_dir, d1, d2, d3;
  int target_value;
  while (Serial.available() > 0) {
    switch (Serial.read()) {
      case 'q':
        adjust(1, 10);
        status(1);
        break;
      case 'a':
        adjust(1, -10);
        status(1);
        break;
      case 'w':
        adjust(2, 10);
        status(2);
        break;
      case 's':
        adjust(2, -10);
        status(2);
        break;
      case 'x':
        motor1_speed = 0;
        motor2_speed = 0;
        status(1);
        status(2);
      case 'L':
        target_dir = sernext(); d1 = sernext(); d2 = sernext(); d3 = sernext();
        if (target_dir != 'f' && target_dir != 'r') {
          Serial.println("bad dir");
          continue;
        }
        target_value = (d1 - '0') * 100 + (d2 - '0') * 10 + (d3 - '0');
        if (target_dir == 'f')      { Motor1_Forward(target_value); }
        else if (target_dir == 'r') { Motor1_Backward(target_value); }
        motor1_dir = (target_dir == 'f') ? 0 : 1;
        motor1_speed = target_value;
        short_status(1);
        break;
      case 'R':
        target_dir = sernext(); d1 = sernext(); d2 = sernext(); d3 = sernext();
        if (target_dir != 'f' && target_dir != 'r') {
          Serial.println("bad dir");
          continue;
        }
        target_value = (d1 - '0') * 100 + (d2 - '0') * 10 + (d3 - '0');
        if (target_dir == 'f')      { Motor2_Forward(target_value); }
        else if (target_dir == 'r') { Motor2_Backward(target_value); }
        motor2_dir = (target_dir == 'f') ? 0 : 1;
        motor2_speed = target_value;
        short_status(2);
        break;
      default:
        break;
    }
  }
}


void setup() {
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENA, OUTPUT);

  pinMode(IN4, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(ENB, OUTPUT);

  digitalWrite(ledPin, HIGH);
  delay(1000);
  digitalWrite(ledPin, LOW);
  delay(1000);


  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  establishContact();

  Serial.write("READY\n");
//  digitalWrite(ledPin, HIGH);
//  delay(500);
//  digitalWrite(ledPin, LOW);
//  delay(500);
//  digitalWrite(ledPin, HIGH);
//  delay(500);
//  digitalWrite(ledPin, LOW);
//  delay(500);
//  digitalWrite(ledPin, HIGH);
//  delay(500);
//  digitalWrite(ledPin, LOW);
//  delay(500);
}

void loop() {
  handleSerial();
  if (motor1_speed == 0) {
    Motor1_Brake();
  } else if (motor1_dir == 1) {
    Motor1_Backward(motor1_speed);
  } else if (motor1_dir == 0) {
    Motor1_Forward(motor1_speed);
  }

  if (motor2_speed == 0) {
    Motor2_Brake();
  } else if (motor2_dir == 1) {
    Motor2_Backward(motor2_speed);
  } else if (motor2_dir == 0) {
    Motor2_Forward(motor2_speed);
  }

  
  
  //Serial.write("Looped.\n");
//  Motor1_Brake();
//  Motor2_Brake();
//  delay(100);
//  Motor1_Forward(50);
//  Motor2_Forward(200);
//  delay(1000);
//  Motor1_Brake();
//  Motor2_Brake();
//  delay(100);
//  Motor1_Backward(50);
//  Motor2_Backward(200);
//  delay(1000);
}

void Motor1_Forward(int Speed)
{
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, Speed);
}

void Motor1_Backward(int Speed)
{
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  analogWrite(ENA, Speed);
}
void Motor1_Brake()
{
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
}
void Motor2_Forward(int Speed)
{
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(ENB, Speed);
}

void Motor2_Backward(int Speed)
{
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  analogWrite(ENB, Speed);
}
void Motor2_Brake()
{
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}
