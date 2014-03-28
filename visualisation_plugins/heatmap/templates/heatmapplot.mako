<%
    default_title = "Heatmapplot of '" + hda.name + "'"
    info = hda.name
    if hda.info:
        info += ' : ' + hda.info

    # optionally bootstrap data from dprov
    ##data = list( hda.datatype.dataset_column_dataprovider( hda, limit=10000 ) )

    # Use root for resource loading.
    root = h.url_for( '/' )
%>
## ----------------------------------------------------------------------------

<!DOCTYPE HTML>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>${title or default_title} | ${visualization_display_name}</title>
<script type="text/javascript" src="/plugins/visualizations/heatmap/static/js/jquery-1.9.1.min.js"></script>
<script type="text/javascript" src="/plugins/visualizations/heatmap/static/js/d3.v3.min.js"></script>
<script type="text/javascript" src="/plugins/visualizations/heatmap/static/js/Biojs.js"></script>
<script type="text/javascript" src="/plugins/visualizations/heatmap/static/js/Biojs.HeatmapViewer.js"></script>

<script>
$(document).ready(function(){
var painter = new Biojs.HeatmapViewer({
                        jsonData:
        [{
            "col": 0,
            "row": 0,
            "label": "M",
            "score": 27,
            "row_label": "A"
        }, {
            "col": 0,
            "row": 1,
            "label": "M",
            "score": 5,
            "row_label": "C"
        }, {
            "col": 1,
            "row": 0,
            "label": "M",
            "score": 43,
            "row_label": "D"
        }, {
            "col": 1,
            "row": 1,
            "label": "M",
            "score": 58,
            "row_label": "E"
        }],
                        user_defined_config: {
                            colorLow: 'blue',
                            colorMed: 'white',
                            colorHigh: 'red'
                        },
                        target: 'test'
                });
 
});
</script>
</head>

## ----------------------------------------------------------------------------
<body>
<div id="test">
</div>

</body>
</html>
