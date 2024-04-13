#include <bits/stdc++.h>
using namespace std;

bool isPrime(int num)
{
	if(num == 2)
	{
		return true;
	}
	for(int i = 2 ; i<num ; i++)
	{
		if(num%i == 0)
		{
			return false;
		}
	}
	return true;
}
bool isPalin(int num)
{
	int rev = 0;
	while(num != 0)
	{
		int rem = num %10;
		 rev = rev*10 + rem;
		 num /= 10;
	}
	if(rev == num)
	{
		return true;
	}
	else
	{
return false;
	}
}

int main() {
	// Write your code here.
	int N;
	cin >> N;
	for(int i = 2 ; i<= N ; i++ )
	{
		if(isPrime(i) && isPalin(i))
		{
			cout <<i;
		}
	}
}