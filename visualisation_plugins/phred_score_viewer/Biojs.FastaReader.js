Biojs.FastaReader = Biojs.extend ({
    constructor: function (options) {
		var self = this;
		this._container = jQuery( "#" + this.opt.target );
    },	

    opt: {
		start: "",
		end: "",
		current: "",
		
        target: "YourOwnDivId"
    },

    eventTypes: [
		"onSelectionChanged",
		"onScroll",
		"onSelectionChange",
		"onFileLoaded"
    ],

    setSequence: function(startline, endline){
		var sequenceToRender = [];
		while(self.current<=endline){
			currentLine = this.sequences[self.currentline];
			if (currentLine[0]==""){
				self.currentLine +=1;
				continue;
			}
			
		}
		
	},
});
