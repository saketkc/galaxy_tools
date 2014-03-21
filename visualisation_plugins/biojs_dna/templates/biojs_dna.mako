<!DOCTYPE HTML>
<html>
<head>


<script language="JavaScript" type="text/javascript" src="/static/scripts/Biojs.js">
<script language="JavaScript" type="text/javascript" src="/static/scripts/Biojs.Tooltip.js"></script>
<script language="JavaScript" type="text/javascript" src="/static/scripts/Biojs.Sequence.js"></script>
<script language="JavaScript" type="text/javascript" src="/static/scripts/jquery-1.4.2.min.js">
<script language="JavaScript" type="text/javascript" src="/static/scripts/jquery-ui-1.8.2.custom.min.js"></script>

<script type="text/javascript" src="http://code.jquery.com/jquery-1.8.2.min.js"></script>
        <script type="text/javascript">
            jQuery.noConflict();
        </script>
        <script src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.2/jquery-ui.min.js"></script>
        <link rel="stylesheet" href="https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.2/themes/base/jquery.ui.all.css" />
<script type="text/javascript" src="http://www.ebi.ac.uk/Tools/biojs/registry/src/Biojs.js"></script>
        <script type="text/javascript" src="http://www.ebi.ac.uk/Tools/biojs/registry/src/Biojs.Sequence.js"></script>
        <script src="http://www.ebi.ac.uk/Tools/biojs/registry/scripts/Biojs.Tooltip.js"></script>
<script type="text/javascript">
window.onload = function() {
                var theSequence = "gtttgccatcttttgctgctctagggaatccagcagctgtcaccatgtaaacaagcccaggctagaccaGTTACCCTCATCATCTTAGCTGATAGCCAGCCAGCCACCACAGGCAtgagtcaggccatattgctggacccacagaattatgagctaaataaatagtcttgggttaagccactaagttttaggcatagtgtgttatgtaTCTCACAAACATATAAGACTGTGTGTTTGTTGACTGGAGGAAGAGATGCTATAAAGACCACCTTTTAAAACTTCCC-------------------------------AAATACT-GCCACTGATGTCCTG-----ATGGAGGTA-------TGAA-------------------AACATCCACTAAAATTTGTGGTTTATTCATTTTTCATTATTTTGTTTAAGGAGGTCTATAGTGGAAGAGGGAGATATTTGGggaaatt---ttgtatagactagctttcacgatgttagggaattattattgtgtgataatggtcttgcagttaca-cagaaattcttccttattttttgggaa---gcaccaaag----tagggat---aaaatgtcatgatgtgtgcaatacactttaaaatgtttttg-----ccaaaataatt----------------aatgaagc--aaatatggaaa-ataataattattaaatctaggtgatgggtatattgtagttcactatagtattgcacacttttctgtatgtttaaatttttcatttaaaaaaaaactttgagc-----tagacaccaggctatgagctaggagcatagcaatgaccaa----------------------------------------------------------------------------------------------atagactcctaccaa--------------------------------------------------ctc-aaagaatgcacattctCTGGGAAACATGTTTCCATTAGGAAGCCTCGAATGCAATGTGACTGT";
                var mySequence = new Biojs.Sequence({
                    sequence : theSequence,
                    target : "sequenceDiv",
                    format : 'CODATA',
                    id : 'P918283'
                });
            };
</script>

</head>
<body>
        <div id="sequenceDiv" />
    </body>
</html>
