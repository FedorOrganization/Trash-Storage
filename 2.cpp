#include <iostream>
#include <string>

using namespace std;

class Question {
public:
    string questionText;
    string answers[4];
    int correctAnswer;

    Question(string questionText, string answer1, string answer2, string answer3, string answer4, int correctAnswer) {
        this->questionText = questionText;
        this->answers[0] = answer1;
        this->answers[1] = answer2;
        this->answers[2] = answer3;
        this->answers[3] = answer4;
        this->correctAnswer = correctAnswer;
    }
};

class Player {
public:
    string name;
    int score;

    Player(string name) {
        this->name = name;
        this->score = 0;
    }
};

int askQuestion(Player player, Question question) {
    cout << player.name << ", " << question.questionText << endl;
    for (int i = 0; i < 4; ++i) {
        cout << i + 1 << ". " << question.answers[i] << endl;
    }
    int answer;
    cout << "Твой ответ от 1 до 4: ";
    cin >> answer;
    return answer;
}

void showCorrectAnswer(Question question) {
    cout << "Правильный ответ: " << question.answers[question.correctAnswer - 1] << endl;
}

int main() {
    setlocale(LC_ALL, "RU");

    Player player1("Fedor");
    Player player2("Pavel");

    Question questions[3] = {
        Question("Сколько видов линз:", "2", "3", "4", "8", 2),
        Question("Сколько фокусов у линзы:", "2", "3", "4", "8", 2),
        Question("Формула теплоемкости:", "m*c*t", "m*v*g", "v2*m/3", "m*g", 4)
    };

    for (int i = 0; i < 3; ++i) {
        int answer1 = askQuestion(player1, questions[i]);
        int answer2 = askQuestion(player2, questions[i]);

        if (answer1 == questions[i].correctAnswer) {
            player1.score++;
        }
        if (answer2 == questions[i].correctAnswer) {
            player2.score++;
        }

        showCorrectAnswer(questions[i]);
        cout << endl;
    }

    cout << "Баллы:" << endl;
    cout << player1.name << ": " << player1.score << endl;
    cout << player2.name << ": " << player2.score << endl;

    return 0;
}
