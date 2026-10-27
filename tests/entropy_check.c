/* SPDX-License-Identifier: EUPL-1.2
 * entropy_check.c - three-signal filter proof for wendy_prune()
 * Run: gcc tests/entropy_check.c -lm && ./a.out  -> failures = 0
 */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#define ENTROPY_KEEP_X256 819
#define CHUNK 64
#define MAX_REPEATS 2
#define MIN_REPEAT_LINE 24
#define MAX_HASHED_LINES 256
static uint32_t fnv1a(const unsigned char *s, size_t n){uint32_t h=2166136261u;for(size_t i=0;i<n;i++){h^=s[i];h*=16777619u;}return h;}
static uint32_t entropy_x256(const unsigned char *s,size_t n){uint32_t hist[256]={0};for(size_t i=0;i<n;i++)hist[s[i]]++;double h=0.0;for(int b=0;b<256;b++){if(!hist[b])continue;double p=(double)hist[b]/(double)n;h-=p*log2(p);}return (uint32_t)(h*256.0+0.5);}
static int is_ws(const unsigned char *s,size_t n){for(size_t i=0;i<n;i++)if(s[i]!=' '&&s[i]!='\t'&&s[i]!='\r'&&s[i]!='\n')return 0;return 1;}
struct linehist{uint32_t h;uint32_t count;};static struct linehist LH[MAX_HASHED_LINES];
static size_t run_filter(const char *text,size_t *dropped_lines){size_t len=strlen(text),kept=0,dropped=0;for(size_t i=0;i<len;){const unsigned char *line=(const unsigned char*)text+i;const unsigned char *nl=memchr(line,'\n',len-i);size_t n=nl?(size_t)(nl-line+1):(len-i);i+=n;size_t core=n;if(core&&line[core-1]=='\n')core--;if(is_ws(line,core)){dropped++;continue;}if(!nl&&core>CHUNK){size_t ok=1;for(size_t j=0;j+CHUNK<=core;j+=CHUNK)if(entropy_x256(line+j,CHUNK)<ENTROPY_KEEP_X256){ok=0;break;}if(!ok){dropped++;continue;}}if(core>=MIN_REPEAT_LINE){uint32_t h=fnv1a(line,core);int slot=-1,free_slot=-1;for(int k=0;k<MAX_HASHED_LINES;k++){if(LH[k].count==0){if(free_slot<0)free_slot=k;}else if(LH[k].h==h){slot=k;break;}}if(slot<0)slot=free_slot;if(slot>=0){if(LH[slot].count==0)LH[slot].h=h;if(++LH[slot].count>MAX_REPEATS){dropped++;continue;}}}kept+=n;}*dropped_lines=dropped;return kept;}
static int check(const char *name,const char *text,size_t min){memset(LH,0,sizeof(LH));size_t dropped=0,kept=run_filter(text,&dropped),total=strlen(text);int ok=dropped>=min;printf("  %-16s kept %3zu/%3zu bytes, dropped %zu line(s)  %s\n",name,kept,total,dropped,ok?"OK":"FAIL");return ok?0:1;}
int main(void){int f=0;printf("three-signal filter check (repeat <=%d on >=%dB lines, ws-collapse, H>=%.2f)\n",MAX_REPEATS,MIN_REPEAT_LINE,(double)ENTROPY_KEEP_X256/256.0);
f+=check("license-header","Licensed under the EUPL-1.2\nLicensed under the EUPL-1.2\nLicensed under the EUPL-1.2\nLicensed under the EUPL-1.2\nLicensed under the EUPL-1.2\nLicensed under the EUPL-1.2\n",4);
f+=check("whitespace-pad","     \n          \n\t\n              \n                    \n ",5);
f+=check("natural-prose","WENDY is a sovereign research assistant for pollinator ecology and Earth\nobservation. The mesh routes each question to the cheapest capable brain:\nstatute first, local node second, partner cloud last. Prefill burns\nbandwidth, so low-information tokens are pruned before inference begins.\nEach layer is scored by bits per token moved, not by raw clock speed.\n",0);
f+=check("c-code","static uint32_t fnv1a(const unsigned char *s, size_t n) {\n    uint32_t h = 2166136261u;\n    for (size_t i = 0; i < n; i++) { h ^= s[i]; h *= 16777619u; }\n    return h;\n}\n    return h;\n}\n",0);
printf("\nfailures = %d\n",f);return f?1:0;}
-----STOP PASTING HERE, ABOVE THIS LINE IS THE WHOLE FILE-----
