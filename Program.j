.class public Program
.super java/lang/Object
.method public <init>()V
aload_0
invokenonvirtual java/lang/Object/<init>()V
return
.end method
.method public static main([Ljava/lang/String;)V
.limit locals 6
.limit stack 1024
new java/util/Scanner
dup
getstatic java/lang/System.in Ljava/io/InputStream;
invokespecial java/util/Scanner.<init>(Ljava/io/InputStream;)V
astore 0
aload 0
invokevirtual java/util/Scanner.nextInt()I
istore 1
sipush 0
istore 2
sipush 1
istore 3
sipush 1
istore 4
sipush 0
istore 5
l1:
iload 5
iload 1
if_icmpgt l2
iload 2
iload 3
iadd
istore 4
iload 3
istore 2
iload 4
istore 3
iload 5
sipush 1
iadd
istore 5
getstatic java/lang/System/out Ljava/io/PrintStream;
iload 4
invokestatic java/lang/String/valueOf(I)Ljava/lang/String;
invokevirtual java/io/PrintStream/println(Ljava/lang/String;)V
goto l1
l2:
return
.end method
