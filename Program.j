.class public Program
.super java/lang/Object
.method public <init>()V
aload_0
invokenonvirtual java/lang/Object/<init>()V
return
.end method
.method public static main([Ljava/lang/String;)V
.limit locals 4
.limit stack 1024
new java/util/Scanner
dup
getstatic java/lang/System.in Ljava/io/InputStream;
invokespecial java/util/Scanner.<init>(Ljava/io/InputStream;)V
astore 0
aload 0
invokevirtual java/util/Scanner.nextInt()I
istore 1
aload 0
invokevirtual java/util/Scanner.nextInt()I
istore 2
aload 0
invokevirtual java/util/Scanner.nextInt()I
istore 3
iload 1
sipush 0
if_icmpne l3
iload 2
sipush 1
if_icmpne l3
goto l4
l3:
iload 1
sipush 1
if_icmpne l6
iload 2
sipush 0
if_icmpne l6
goto l7
l6:
iload 3
sipush 1
if_icmpeq l1
l7:
l4:
getstatic java/lang/System/out Ljava/io/PrintStream;
sipush 5
invokestatic java/lang/String/valueOf(I)Ljava/lang/String;
invokevirtual java/io/PrintStream/println(Ljava/lang/String;)V
goto l2
l1:
getstatic java/lang/System/out Ljava/io/PrintStream;
sipush 6
invokestatic java/lang/String/valueOf(I)Ljava/lang/String;
invokevirtual java/io/PrintStream/println(Ljava/lang/String;)V
l2:
return
.end method
