using System;
using System.Windows.Forms;
using System.Threading;

class Program {
    static void Main(string[] args) {
        Form f = new Form();
        f.Text = args.Length > 0 ? args[0] : "DiscordMockWindowClass";
        f.Width = 300;
        f.Height = 100;
        Label l = new Label();
        l.Text = "Mock Discord Game Running...\nClose this window to stop.";
        l.AutoSize = true;
        l.Top = 20;
        l.Left = 20;
        f.Controls.Add(l);
        f.FormClosing += (s, e) => { Environment.Exit(0); };
        f.Show();
        Application.Run(f);
    }
}
