from datetime import datetime

def now():
    date=datetime.now().isoformat()
    return date.split(".")[0]
    
def dict2md_table(d,header=['Item','']):
    md_tab=f"|{'|'.join(header)}|"
    md_tab+="\n|-|-|"
    for row in d.items():
        md_row="\n|"
        for x in row:
            if isinstance(x,float): x=f"{x:,.2f}"
            if isinstance(x,int): x=f"{x}"
            if isinstance(x,list): x=", ".join(x)
            md_row+=f"{ x }|"
        md_tab+=md_row
    return md_tab

def read_file(file_path):
    with open(file_path, "r") as file:
        return file.read()
    
def curr(x,precision=2):
    if isinstance(x, (float, int)):
        format_str = f"{{:,.{precision}f}}" if isinstance(x, float) else "{:,}"
        return format_str.format(x)
    else:
        if x==None:
            return '-'
        return x
