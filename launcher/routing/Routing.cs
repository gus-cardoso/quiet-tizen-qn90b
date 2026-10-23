using System;
using System.Runtime.InteropServices;
public static class Routing {
 [DllImport("libcapi-appfw-app-operation-tv.so.0")] static extern int app_operation_get_current_app(string operation,out IntPtr app);
 [DllImport("libcapi-appfw-app-operation-tv.so.0")] static extern int app_operation_set_current_app(string operation,string app);
 [DllImport("libc.so.6")] static extern void free(IntPtr p);
 const string Operation="http://tizen.org/appcontrol/operation/main";
 public static int Main(string[] args) {try{
 IntPtr p;int r=app_operation_get_current_app(Operation,out p);
 string current=p==IntPtr.Zero?"":Marshal.PtrToStringAnsi(p);if(p!=IntPtr.Zero)free(p);
 Console.WriteLine("get_result="+r+" home="+current);if(r!=0)return 2;
 if(args.Length==0)return 0;
 if(args.Length!=3||args[0]!="set"||current!=args[1])return 3;
 if(args[2]!="QuietHome1.Home"&&args[2]!="com.samsung.tv.csfs")return 4;
 r=app_operation_set_current_app(Operation,args[2]);Console.WriteLine("set_result="+r);if(r!=0)return 5;
 r=app_operation_get_current_app(Operation,out p);current=p==IntPtr.Zero?"":Marshal.PtrToStringAnsi(p);if(p!=IntPtr.Zero)free(p);
 Console.WriteLine("verify_result="+r+" home="+current);return r==0&&current==args[2]?0:6;
 }catch(Exception e){Console.WriteLine(e);return 7;}}
}
