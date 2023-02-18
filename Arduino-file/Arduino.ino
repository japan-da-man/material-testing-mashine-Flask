long saisyo = 0;

//モータードライバーとArduinoピンの接続関係//
int APHASE = 2;
int AENBL = 3;
int BPHASE = 4;
int BENBL = 5;
//Arduinoピンは，好きな場所（数字）で接続してください//

//ロードセルとArudinoピンの接続関係//
int dat = 10;
int clk = 11;
//Arduinoピンは，好きな場所（数字）で接続してください//


void setup() {
    Serial.begin(9600);

    pinMode(APHASE, OUTPUT);
    digitalWrite(APHASE, HIGH);

    pinMode(AENBL, OUTPUT);
    digitalWrite(AENBL, HIGH);

    pinMode(BPHASE, OUTPUT);
    digitalWrite(BPHASE, HIGH);

    pinMode(BENBL, OUTPUT);
    digitalWrite(BENBL, HIGH);

    pinMode(clk, OUTPUT);
    pinMode(dat, INPUT);

    delay(100);

    //物がなにも置かれていない状態を測定する//
    for (char i = 0; i < 24; i++) {
        digitalWrite(clk, 1);
        delayMicroseconds(1);
        digitalWrite(clk, 0);
        delayMicroseconds(1);

        saisyo = (saisyo << 1) | (digitalRead(dat));
    }
//ロードセルとArduinoで，2進数の扱い方が異なるため，排他的論理和を用いてそろえる//
    saisyo = saisyo ^ 0x800000;
}
//以上の処理で，saisyo に，物が何も置かれていない状態の荷重を代入される//

//ステッピングモーターを回し，ロードセルから荷重を読みとる//
void loop() {

    byte var;
    long atai = 0;

    digitalWrite(APHASE, HIGH);
    delay(10);
    digitalWrite(BPHASE, HIGH);
    delay(10);

    digitalWrite(APHASE, LOW);
    delay(10);
    digitalWrite(BPHASE, LOW);
    delay(10);


    for (char i = 0; i < 24; i++) {
        digitalWrite(clk, 1);
        delayMicroseconds(1);
        digitalWrite(clk,0);
        delayMicroseconds(1);

        atai = (atai << 1) | (digitalRead(dat));

    }

//ロードセルとArduinoで，2進数の扱い方が異なるため，排他的論理和を用いてそろえる//
   atai = atai^0x800000;

    long omosa;
    omosa = ((atai - saisyo)/1000 - 59)*3.5*9.8/1000 ;//何も置かれていない時に0[N]になるように，補正する//
    Serial.println(omosa);//シリアルポートに荷重[N]を出力する//

    delay(300);
}
