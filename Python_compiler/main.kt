#core: CtOs_Old
#target: ARM32
#define: AUDIO_CHIP 0x3F0040A2

function ЗапускСистемы() {
    net_flush;
    out_cell(AUDIO_CHIP, 0x00000001);
    terminate;
}
