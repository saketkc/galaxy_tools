<!DOCTYPE HTML>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <title>${hda.name} | ${visualization_name}</title>
        <script type="text/javascript" src="/plugins/visualizations/inchlib/static/jquery-2.0.3.min.js"></script>
        <script type="text/javascript" src="/plugins/visualizations/inchlib/static//kinetic-v5.0.0.min.js"></script>
        <script type="text/javascript" src="/plugins/visualizations/inchlib/static/Biojs.js"></script>
        <script type="text/javascript" src="/plugins/visualizations/inchlib/static/Biojs.InCHlib.js"></script>
        <script type="text/javascript">
            (function ($) {
                var instance;
                $(document).ready(function () {
                     var hdaJson = ${h.to_json_string( trans.security.encode_dict_ids( hda.to_dict() ), indent=2 )};
                     console.log(hdaJson);
                     var vis_id = hdaJson["id"];
                    var xhr = jQuery.getJSON( "/api/datasets/"+ vis_id, {
                        data_type : 'raw_data',
                        provider  : 'base',
                        });
                    //var xhr = jQuery.getJSON("/api/datasets/417e33144b294c21?data_type=raw_data&provider=column");
                    instance = new Biojs.InCHlib({
                        target : "inchlib",
                        metadata: false,
                        max_height: 800,
                        width: 700,
                        metadata_colors: "RdLrBu"
                        });
                    xhr.done( function( response ){
                        var data= response.data;
                        data  = data.join("");
                        instance.read_data(JSON.parse(data));
                        instance.draw();
            });
                    });
                })(jQuery);
        </script>
    </head>

    <body>
        <div id="inchlib"></div>
    </body>
</html>

