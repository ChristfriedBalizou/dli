"use strict";

var page = (function(page){

    var $scrollTopBtn = $("#scroll-top");
    var $container = $("#prerelation-page-container");
    
    var $statisticContainer = $(".statistic-container");
    var $statistic = $(".statistic");

    var $databases = $("#databases");
    var AutoCompletElement;

	class ChipsElement extends React.Component {
		constructor(props) {
			super(props);
			this.state = {data: this.props.selected || []};

			this.handleClick = this.handleClick.bind(this);
		}

		handleClick(e) {
			var value = e.target.dataset.value;
			var list = this.state.data;
			var i = list.indexOf(value);

			if(i === -1){
				return;
			}

			list.splice(i, 1);
			this.setState({data: list});
			this.props.selectedChanged(list);
		}

		componentDidMount() {
			var $el = ReactDOM.findDOMNode(this);
			componentHandler.upgradeElements($el);
		}

		render () {
			return (
				this.state.data.length > 0 ? 
				(React.createElement(
					"div",
					{className: "chips-container"},
					this.state.data.map(value =>
						(React.createElement(
							"span",
							{className:"mdl-chip mdl-chip--deletable",
                             key: value + "_chip"},
							React.createElement(
								"a", 
								{className:"mdl-chip__text no-decoration",
                                 href:"/#table/" + value},
								value),
							React.createElement(
								"button",
								{className: "mdl-chip__action", 
									onClick: this.handleClick},
								React.createElement(
									"i", 
									{className: "material-icons", 
										"data-value": value},
									"cancel"))))),
					React.createElement(
						"a", 
						{href : "/#relation/" + this.state.data.join('/'),
							className: "mdl-button mdl-js-button mdl-color-text--indigo"},
						"View relations"))) : React.createElement("div", null)
			);
		}
	}


	class SelectableList extends React.Component {
		constructor(props) {
			super(props);
			this.state = {dataSource: this.props.dataSource, 
				selected: this.props.selected || []};

			this.handleChange = this.handleChange.bind(this);
		}


		handleChange(e) {
			this.props.updateSelection(e.target.dataset.value);
		}

		componentDidMount() {
			var $el = ReactDOM.findDOMNode(this);
			componentHandler.upgradeElements($el);
		}

		render() {
			return (
				React.createElement(
					"ul",
					{className: "wide mdl-list no-margin"},
					this.state.dataSource.map(
						value => 
						React.createElement(
							"li", 
							{key: value, 
								className: "mdl-list__item"},
							React.createElement(
								"span", 
								{className:"mdl-list__item-primary-content"}, 
								value),
							React.createElement(
								"span", 
								{className:"mdl-list__item-secondary-action"},
								React.createElement(
									"label",
									{className: "mdl-switch mdl-js-switch", 
										for: value},
									React.createElement(
										"input",
										(this.state.selected.indexOf(value) === -1 ?
											{type: "checkbox",
												className:"mdl-switch__input",
												id: value,
												"data-value": value,
												onChange: this.handleChange}:
											{type: "checkbox",
												className:"mdl-switch__input",
												id: value,
												"data-value": value,
												onChange: this.handleChange,
												checked: true})
									)
								)
							)
						)
					)
				)
			);
		}
	}

	class PanelComponent extends React.Component {
		constructor(props) {
			super(props);
			this.state = {showPanel: false, 
				dataSource: this.props.dataSource, 
				selected: this.props.selected || []};

			this.handleClick = this.handleClick.bind(this);
			this.updateSelection = this.updateSelection.bind(this);
		}

		handleClick(e) {
			e.preventDefault();
			this.setState({ showPanel: !this.state.showPanel});
		}

		updateSelection(value) {
			this.props.updateSelection(value);
		}

		componentDidMount() {
			var $el = ReactDOM.findDOMNode(this);
			componentHandler.upgradeElements($el);
		}

		render () {
			return (
				React.createElement(
					"div", 
					null,
					React.createElement(
						"button",
						{className: "accordion", 
							onClick:this.handleClick},
						"View all tables",
						React.createElement(
							"i",
							{className:"material-icons"},
							("keyboard_arrow_" + (this.state.showPanel ? "up": "down")))),
					React.createElement(
						"div", 
						{className: "content " + (this.state.showPanel ? "active": "" )},
						(this.state.showPanel ? 
							React.createElement(
								"div", 
								{className: "panel"},
								React.createElement(
									SelectableList,
									{dataSource: this.state.dataSource,
										selected: this.state.selected,
										updateSelection: this.updateSelection})) : 
							null)))
			);
		}
	}


	class InputField extends React.Component {
		constructor(props) {
			super(props);
			this.state = {dataSource: this.props.dataSource};
		}

		componentDidMount() {
			var self = this;  
			var $el = ReactDOM.findDOMNode(self);
			var $typeahead = $($el).find('input');

			componentHandler.upgradeElements($el);

            $typeahead.typeahead({
                hint: true,
                highlight: true,
                minLength: 1
            },
            {
                name: 'tables',
                source: substringMatcher(self.state.dataSource)
            });

			$typeahead.on('typeahead:selected', function(event, selection) {
				self.props.onSelected(selection);
				$typeahead.typeahead('val', '')
					.closest(".is-dirty")
					.removeClass('is-dirty');
			});
		}

		render() {
			return (
				React.createElement(
					"div",
					{className: "no-padding-bottom mdl-textfield mdl-js-textfield"},
					React.createElement(
						"input",
						{className: "mdl-textfield__input wide",
							id: "search-field",
							autofocus:true}),
					React.createElement(
						"label",
						{className:"mdl-textfield__label", 
							for:"search-field"},
						React.createElement(
							"i", 
							{className: "material-icons"},
							"search"),
						"Type here to select tables..."))
			);
		}

	}

	class AutoCompleter extends React.Component {

		constructor(props) {
			super(props);

			this.state = {dataSource: this.props.dataSource, selected: []};

			this.handleSelected = this.handleSelected.bind(this);
			this.handleChipsChange = this.handleChipsChange.bind(this);
			this.updateSelection = this.updateSelection.bind(this);
		}

		componentDidMount() {
			var $el = ReactDOM.findDOMNode(this);
			componentHandler.upgradeElements($el);
		}

		updateSelection (value) {
			var list = this.state.selected;
			var i = list.indexOf(value);

			if(i === -1) {
				list.push(value);
			} else {
				list.splice(i, 1);
			}

			this.setState({selected: list});
		}

		handleChipsChange(selectList) {
			this.setState({selected: selectList || []});
		}

		handleSelected(selection) {
			var list = this.state.selected;
			var i = list.indexOf(selection);

			if(i === -1){
				list.push(selection);
				this.setState({selected: list});
			}
		}

		render() {
			return (
				React.createElement(
					"div",
					null,
					React.createElement(
						"div",
						{className: "mdl-card mdl-card mdl-shadow--2dp"}, 
						React.createElement(
							"div",
							{className: "wide no-padding  pad-left-1 mdl-card__supporting-text"},
							React.createElement(
								InputField,
								{dataSource: this.state.dataSource,
									onSelected: this.handleSelected}),
							React.createElement(
								ChipsElement, 
								{selected: this.state.selected,
									selectedChanged: this.handleChipsChange})),
						React.createElement(
							"div", 
							{className:"mdl-card__actions no-padding mdl-card--border"},
							React.createElement(
								PanelComponent,
								{dataSource: this.state.dataSource,
									selected: this.state.selected,
									updateSelection: this.updateSelection}))))
			);
		}
	}


    page.prerelation = {

        init: function() {

            // handle scroll top button
            $("main").scroll(scrollFunction);
            $scrollTopBtn.click(function(){
                $("main").animate({scrollTop: 0}, 200);
            });

            $databases.on("change", function(){
                cache.getInstance().remove("tables");
                cache.getInstance().remove("statistics");
                page.prerelation.render();
            });
            return this;
        },

        render: function() {

            
            // Load table list
            if(!cache.getInstance().hasData("tables")) {
                server.getTableList()
                    .done(function(data){
                        //Todo common response handler
                        if(data.status != true) {
                            console.error(data.response.message)
                            return;
                        }

                        if(AutoCompletElement) {
                            ReactDOM.unmountComponentAtNode($container[0]);
                        }

                        AutoCompletElement = ReactDOM.render(
                            React.createElement(AutoCompleter, {dataSource: data.response.data}), 
                            $container[0]);

                        cache.getInstance().add("tables", data.response.data);
                    });
            }
            
            
            // Load statistics information
            if(!cache.getInstance().hasData("statistics")) {
                server.getStatistics()
                    .done(function(data){
                        //TODO common response handler
                        if(data.status != true) {
                            console.error(data.response.message)
                            return;
                        }

                        var msg = "Loaded ";
                        msg += data.response.data.tables_number;
                        msg += " tables in " + data.elapsed_time;
                        
                        $statistic.text(msg + ".");
                        cache.getInstance().add("statistics", data.response.data);
                    })
                    .always(loader.start({container: $statisticContainer,
                        element: $statistic}));
            }

            return this;
        }
    };

    function scrollFunction() {
        if (document.querySelector("main").scrollTop > 20 ) {
            $scrollTopBtn.show();
        } else {
            $scrollTopBtn.hide();
        }
    }


    function substringMatcher (dataSource) {
        return function findMatches(q, callback) {
            var matches, substringRegex;

            // an array that will be populated with substring matches
            matches = [];

            // regex used to determine if a string contains the substring `q`
            var substrRegex = new RegExp(q, 'i');

            // iterate through the pool of strings and for any string that
            // contains the substring `q`, add it to the `matches` array
            $.each(dataSource, function(i, str) {
                if (substrRegex.test(str)) {
                    matches.push(str);
                }
            });

            matches.sort(function(a, b){
                return a.length - b.length;
            });

            callback(matches);
        };
    }


    return page;

})(page || {});
