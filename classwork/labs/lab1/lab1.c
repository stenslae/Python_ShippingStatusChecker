#include <stdio.h>

int main(void){
    printf("Hours and minutes since power outage? (e.g., 2 30 for 2 hours, 30 minutes)");
    scanf("%d %d", &hours, &minutes);
    double time = hours + minutes/60;
    
    int calc = 2;

    printf("Estimated ", calc, "ipsum");
    return 0;
}
