// Пины для подключения к MangoPi
const int PIN_OUT = 4;
const int PIN_IN  = 2;

// Временные интервалы
const unsigned long PULSE_DURATION_US = 500;
const unsigned long TIMEOUT_US        = 5000;

// Количество измерений
const int LATENCY_COUNT = 2;

// Времена фронтов
volatile unsigned long edgeTimes[LATENCY_COUNT];
volatile int edgeIndex = 0;

unsigned long pulseTimes[LATENCY_COUNT];

unsigned long count = 1;

// Прерывание по обоим фронтам
void onSignalChange() {
	if (edgeIndex < LATENCY_COUNT) {
		edgeTimes[edgeIndex++] = micros();
	}
}

void setup() {
	Serial.begin(115200);

	pinMode(PIN_OUT, OUTPUT);
	pinMode(PIN_IN, INPUT);

	digitalWrite(PIN_OUT, LOW);

	attachInterrupt(
		digitalPinToInterrupt(PIN_IN),
		onSignalChange,
		CHANGE
	);

	delay(2000);
}

void loop() {
	bool isTimeout = false;

	// Сброс состояния
	noInterrupts();
	edgeIndex = 0;
	interrupts();

	// Первый фронт
	pulseTimes[0] = micros();
	digitalWrite(PIN_OUT, HIGH);

	// Держим импульс
	while (micros() - pulseTimes[0] < PULSE_DURATION_US) {
	}

	// Второй фронт
	pulseTimes[1] = micros();
	digitalWrite(PIN_OUT, LOW);

	// Ждем оба фронта ответа
	unsigned long waitStart = micros();

	while (edgeIndex < LATENCY_COUNT) {
		if (micros() - waitStart > TIMEOUT_US) {
			isTimeout = true;
			break;
		}
	}

	// Вывод
	if (isTimeout) {
		Serial.print("ERROR;Timeout;");
		Serial.println(count);
	}
	else {
		Serial.print("DATA;");
		Serial.print(count);

		// Просто отправляем задержки подряд
		for (int i = 0; i < LATENCY_COUNT; i++) {
			long latency = edgeTimes[i] - pulseTimes[i];

			Serial.print(";");
			Serial.print(latency);
		}

		Serial.println();
	}

	count++;

	delay(1);
}