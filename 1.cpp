#include <iostream>
#include <string>

using namespace std;


class Question
{
public:
    string Question1;
    string Answer1; 
    string Answer2;
    string Answer3;
    string Answer4;
    int AnswerNum;

    Question(string Question1, string Answer1, string MaybeAnswer1)
    {
        this->Question1;
        this->Answer1;
        this->Answer2;
        this->Answer3;
        this->Answer4;
        this->AnswerNum;

    }

    void Game(Player, string name, string Question1, string Answer1, string Answer2, string Answer3, string Answer4, string MaybeAnswer1)
    {
        
    }
};


class Player
{
public:
    string name;

    Player(string name)
    {
        this->name = name;
    }

};


int main(Player, Question, string Question1,string Answer1,string Answer2,string Answer3,string Answer4,int AnswerNum;)
{
    setlocale(LC_ALL, "RU");

    Player* Player1 = new Player("Fedor");
    Player* Player2 = new Player("Pavel");
    
    Question* question1 = new Question ("Сколько видов линз: ", "2", "3", "4", "8", 2);
    Question* question2 = new Question ("Сколько фокусов у линзы: : ", "2", "3", "4", "8", 2);
    Question* question3 = new Question ("Формула теплоемкости: ", "m*c*t", "m*v*g", "v2*m/3", "m*g", 2);
    




   

    return 0;
}

