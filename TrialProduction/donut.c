k;
double sin(),cos();
main() {
    // R1 = 1, R2 = 2, K1 = 30, K2 = 5
    float A = 0,
          B = 0,
          i,
          j,
          z[1760]; // 1760 = 22 * 80
    char b[1760];
    printf("\x1b[2J");
    for(;;) {
        memset(b,32,1760); // char 32 = ' '
        memset(z,0,7040); // 7040 = 22 * 4 * 80(because type float is 4 byte)
        for(j=0; 6.28>j; j+=0.07)
            for(i=0; 6.28>i; i+=0.02) {
                float c = sin(i), // sinphi
                      d = cos(j), // costheta
                      e = sin(A), // sinA
                      f = sin(j), // sintehta
                      g = cos(A), // cosA
                      h = d+2, // circlex = costheta + 2
                      D = 1/(c*h*e+f*g+5), // ooz = sinphi * circlex * sinA + sintheta * cosA + 5
                      l=cos(i), // cosphi
                      m=cos(B), // cosB
                      n=sin(B), // sinB
                      t=c*h*g-f*e; // sinphi * circlex * cosA - sintheta * sinA
                // base place = (40, 12)
                int x=40+30*D*(l*h*m-t*n), // 40 + 30 * D * (cosphi * circlex * cosB - t * sinB)
                    // maybe 15 means K1 / 2
                    y=12+15*D*(l*h*n+t*m), // 12 + 15 * D * (cosphi * circlex * sinB + t * cosB)
                    o=x+80*y, // 
                    N=8*((f*e-c*d*g)*m-c*d*e-f*g-l*d*n);
                // 22 > y && y > 0 && 80 > x && x > 0 && D > z[o](o = x + 80 * y)
                if(22>y&&y>0&&x>0&&80>x&&D>z[o]){
                    z[o]=D;
                    b[o]=".,-~:;=!*#$@"[N>0?N:0];
                }
            }
        /*#****!!-*/
        printf("\x1b[H");
        for(k=0;1761>k;k++)
            putchar(k%80?b[k]:10); // 10 is linefeed
        A+=0.07;
        B+=0.02;
    }
}
/*****####*******!!=;:~
       ~::==!!!**********!!!==::-
         .,~~;;;========;;;:~-.
             ..,--------,*/
