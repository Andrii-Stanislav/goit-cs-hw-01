.MODEL small
mov ax, b ; AX = b
sub ax, c ; AX = b - c
add ax, a ; AX = b - c + a
mov result, ax


mov dx, OFFSET msgRes
mov ah, 09h
int 21h


mov ax, result
call print_int16_signed


mov dx, OFFSET nl
mov ah, 09h
int 21h


mov ax, 4C00h
int 21h


print_int16_signed PROC
push bx
push cx
push dx


or ax, ax
jns pis_positive
neg ax
mov dl, '-'
mov ah, 02h
int 21h
pis_positive:
cmp ax, 0
jne pis_convert
mov dl, '0'
mov ah, 02h
int 21h
jmp pis_done


pis_convert:
xor cx, cx
pis_divloop:
xor dx, dx
mov bx, 10
div bx
push dx
inc cx
cmp ax, 0
jne pis_divloop


pis_printloop:
pop dx
add dl, '0'
mov ah, 02h
int 21h
loop pis_printloop


pis_done:
pop dx
pop cx
pop bx
ret
print_int16_signed ENDP


END start