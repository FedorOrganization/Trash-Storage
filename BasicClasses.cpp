#include <iostream>
#include <string>

using namespace std;

class Student
{
public:

	string name;
	int age;
	float avarage;
	string smth;

public:
	Student(string name, int age, float avarage)
	{
		this->age = age;
		this->name = name;
		this->avarage = avarage;

	}

	void Status()
	{
	
		if (avarage >= 4.6)
		{
			cout << name << endl << "otlichnik, straight A student\n";
		}
		if (avarage < 3.6)
		{
			cout << name << " " << "Bad Person\n";
						 
		}
		if (avarage >= 3.6)
		{
			cout << name << " " << "Middle Person\n";
		}
		
	}
};

int main()
{
	Student* Mark = new Student("Mark", 13, 3.5);
	Student* Pavel = new Student("Pavel", 16, 4.7);

	Mark->Status();
	Pavel->Status();

	delete Mark;
	delete Pavel;

	return 0;
}

