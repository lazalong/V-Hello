import os

fn main() {
	println('test')

	b := 4

	// The value of `a` is for me: "d:\Documents\_Projects\_VLang\projects\01_Hello\hello.exe"
	a := os.args.clone()

	c := 5

	d := b + c

	println('hello world: $b $c $a $d')

}
