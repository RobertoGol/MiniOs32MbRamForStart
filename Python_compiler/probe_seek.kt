#target: ARM32

#define: STREAM_EMIT_CELL 0x00F00FF0
#define: FILE_SEEK 0x00000136

pub entry main(cell:raw args) {
    Stream_Emit = 0x0000001A;
    sys_call(FILE_SEEK);
    terminate;
}
