var relations = (function(){

    "use strict";

    var Element;

    class Column extends React.Component {

        constructor(props) {
            super(props);

            this.state = {text: '', table: this.props.table};
            this.handleChange = this.handleChange.bind(this);
        }

        componentDidMount() {
            var self = this;
            var $el = $(ReactDOM.findDOMNode(self)).find("input");

            // prepare auto complete here
            var dataSource = new Bloodhound({
                datumTokenizer: Bloodhound.tokenizers.whitespace,
                queryTokenizer: Bloodhound.tokenizers.whitespace,
                prefetch: {
                    url: "/columns/" + this.state.table,
                    cache: false,
                    filter: function(data) {
                        return data.response.data
                    }
                }
            });

            $el.typeahead({
                highlight: true
            }, {
                name: this.props.table + "-typeahead",
                source: dataSource
            });

            $el.on('typeahead:selected', function(event, selection) {
                self.setState({text: selection});
                self.props.onChange(selection);
            });

            $el.on('focus',function(){
                $el.closest(".form-container").find('.form-label')
                   .addClass("active")
                   .siblings()
                   .addClass("active");
            }).on('blur',function(){
                if (!!$(this).val()){
                }else{
                    $el.closest(".form-container").find(".form-label")
                       .removeClass("active")
                       .siblings()
                       .removeClass("active");
                }
            });

        }

        handleChange(e) {
            this.setState({ text: e.target.value});
            this.props.onChange(e.target.value);
        }

        render() {
            return (
                React.createElement("div",
                    {className: "form-container"},
                    React.createElement("input", 
                        {onChange: this.handleChange,
                         value: this.state.text,
                         className: "form-control typeahead",
                         id: this.state.table}),
                    React.createElement("label", {className: "form-label", 
                                                  for: this.state.table}, this.state.table))
            );
        }

    }

    class ColumnsAdderElement extends React.Component {
        constructor(props) {
            super(props);

            this.state = {leftCol: '',
                          rightCol: '',
                          leftTable: this.props.leftTable,
                          rightTable: this.props.rightTable};

            this.handleSubmit = this.handleSubmit.bind(this);
            this.handleLeftColChange = this.handleLeftColChange.bind(this);
            this.handleRightColChange = this.handleRightColChange.bind(this);
            this.handleHide = this.handleHide.bind(this);
        }


        componentDidMount() {
            var $el = ReactDOM.findDOMNode(this);
            componentHandler.upgradeElements($el);
        }

        handleSubmit(e) {
            e.preventDefault();

            if(!this.state.leftCol || /^\s*$/.test(this.state.leftCol)) {
                snackbar.show("Missing "+ this.state.leftTable +" column");
                return;
            }

            if(!this.state.rightCol || /^\s*$/.test(this.state.rightCol)) {
                snackbar.show("Missing "+ this.state.rightTable +" column");
                return;
            }
            
            var newItem = {"left": this.state.leftCol,
                           "right": this.state.rightCol,
                           "is_deleted": false,
                           "user": loginSession.user(),
                           "record_date": (new Date()).toISOString().replace("T", ' ').split(".")[0],
                           "relation_type": "human"}

            this.props.onSubmit(newItem);
            this.setState({leftCol: '', rightCol: ''});
        }

        handleLeftColChange(value) {
            this.setState({leftCol: value});
        }
        
        handleRightColChange(value) {
            this.setState({rightCol: value});
        }

        handleHide(e) {
            this.props.hideAddCol();
        }

        render () {
            return (
                React.createElement("form",
                    {onSubmit: this.handleSubmit},
                    React.createElement("div", {className: "mdl-grid no-margin no-padding"},
                        React.createElement("div", {className: "mdl-cell mdl-cell--6-col"},
                            React.createElement(Column, 
                                {onChange: this.handleLeftColChange, table: this.state.leftTable})
                        ),
                        React.createElement("div", {className: "mdl-cell mdl-cell--6-col"},
                            React.createElement(Column, 
                                {onChange: this.handleRightColChange, table: this.state.rightTable})
                        ),
                        React.createElement("div", {className: "mdl-cell mdl-cell--12-col"},
                            React.createElement("button",
                                {className: "right mdl-button mdl-js-button mdl-button--raised mdl-color--indigo mdl-color-text--white"}, "Add"),
                            React.createElement("button",
                                {type: "button",
                                 onClick: this.handleHide,
                                className: "right mdl-button mdl-js-button mdl-button--raised mdl-color--pink mdl-color-text--white"}, "Cancel")
                        )
                        )
                    )
            );
        }
    }

    class Relation extends React.Component {
        constructor(props) {
            super(props);
            this.state = {field: this.props.field,
                          tableLeft: this.props.tableLeft,
                          tableRight: this.props.tableRight}

            this.handleCheckboxChange = this.handleCheckboxChange.bind(this, this.state);
            this.handleCheckboxClick = this.handleCheckboxClick.bind(this);
        }

        componentDidMount() {
            var $el = ReactDOM.findDOMNode(this);
            componentHandler.upgradeElements($el);
        }

        getFieldKey() {
            return this.props.id 
                 + this.state.field.left 
                + this.state.field.right;
        }

        getLabel() {
            var a = this.state.field.left;
            var b = this.state.field.right;

            if(a === b) {
                return React.createElement(
                    'a',
                    {className: "no-decoration", href: "/#column/" + a},
                    a
                );
            }

            return (
                React.createElement('div', null,
                    React.createElement(
                        'a',
                        {className: "no-decoration", href: "/#column/" + a},
                        a
                    ),
                    " - ",
                    React.createElement(
                        'a',
                        {className: "no-decoration", href: "/#column/" + b},
                        b
                    )
                )
            );
        }

        handleCheckboxClick(e) {
            var $el = ReactDOM.findDOMNode(this);
            var $mdlSwitch = $($el).find(".mdl-js-switch")[0];
            
            e.preventDefault();
            this.handleCheckboxChange(this.state);

            if (this.state.field.is_deleted === true) {
                $mdlSwitch.MaterialSwitch.off();
                return;
            }
            $mdlSwitch.MaterialSwitch.on();
        }

        handleCheckboxChange(obj) {
            obj.field.relation_type = "human";
            obj.field.is_deleted = !obj.field.is_deleted;
            
            updateOrCreate(obj.tableLeft, obj.tableRight, obj.field);
            
            this.setState(prevState => ({
                field : obj.field
            }));
        }

        render() {
            return (
                React.createElement(
                    "li",
                    {key: this.getFieldKey(), className: "mdl-list__item", id: this.getFieldKey()},
                    React.createElement("span",
                        {className: "mdl-list__item-primary-content relation-link"},
                        this.getLabel()),
                    React.createElement("span",
                        {className: "mdl-list__item-secondary-action"},
                        React.createElement("label",
                            {className: "mdl-switch mdl-js-switch",
                                "for": this.getFieldKey(),
                                onClick: this.handleCheckboxClick
                            },
                            React.createElement("input", {type: 'checkbox',
                                className: "mdl-switch__input",
                                id: this.getFieldKey(),
                                defaultChecked: !this.state.field.is_deleted,
                            }),
                            React.createElement("span", {className: "mdl-switch__label"}),
                        )
                    ),
                    this.state.field.user ? (React.createElement(
                        "div",
                        {className: "mdl-tooltip mdl-tooltip--top text-left",
                         for: this.getFieldKey()},
                        React.createElement(
                            "strong",
                            null,
                            "Created by " + this.state.field.user.firstName + " " + this.state.field.user.lastName
                        ),
                        React.createElement("br", null),
                        "on " + this.state.field.record_date
                    )) : null
                )
            );
        }
    }

    
    class RelationTalbe extends React.Component {

        constructor(props) {
            super(props);
            this.state = {relation: this.props.relation,
                          fields: this.props.fields,
                          showAddColForm: false};

            this.handleColSubmit = this.handleColSubmit.bind(this);
            this.handleAddClick = this.handleAddClick.bind(this);
            this.handleShowAddColForm = this.handleShowAddColForm.bind(this);
        }


        componentDidMount() {
            var $el = ReactDOM.findDOMNode(this);
            componentHandler.upgradeElements($el);
        }

        handleColSubmit(newItem) {
            // submit new item to server
            this.setState(prevState => ({
                fields: prevState.fields.concat(newItem),
            }));
            
            this.setState({ showAddColForm: false });
            updateOrCreate(this.state.relation.a, this.state.relation.b, newItem);
        }

        handleShowAddColForm(e) {
            this.setState({ showAddColForm: false });
        }

        handleAddClick(e) {
            this.setState({ showAddColForm: true });
        }

        getRelationKey() {
            return this.state.relation.a + this.state.relation.b;
        }

        getLabel() {
            return this.state.relation.a + ' - ' +this.state.relation.b;
        }

        render() {
            return (
                React.createElement(
                    "div",
                    null,
                    React.createElement(
                        "span",
                        {key: this.getRelationKey(), className: "mdl-chip"},
                        React.createElement(
                            "span",
                            {className: "mdl-chip__text relation-link-header mdl-chip--deletable"},
                            this.getLabel()),
                        React.createElement("button",
                            {type: "button", className: "mdl-chip__action"},
                            React.createElement("i",
                                {className: "material-icons mdl-color-text--indigo",
                                onClick: this.handleAddClick}, "add_circle"))
                    ),
                    React.createElement(
                        "ul",
                        {className: "no-margin no-padding mdl-list"},
                        (this.state.showAddColForm ? React.createElement("li", {className: "mdl-list__item editor"},
                            React.createElement(ColumnsAdderElement,
                                {onSubmit: this.handleColSubmit,
                                 hideAddCol: this.handleShowAddColForm,
                                 leftTable: this.state.relation.a,
                                 rightTable: this.state.relation.b})) : null),
                        this.state.fields.map(field => React.createElement(
                            Relation, {field: field,
                                       id: this.getRelationKey(),
                                       tableLeft: this.state.relation.a,
                                       tableRight: this.state.relation.b})
                        ))
                )
            )
        }
    }


    class RelationElement extends React.Component {

        constructor(props) {
            super(props);
            this.state = {relations: this.props.relations};
        }

        render() {
            return (React.createElement(
                'div',
                null,
                this.state.relations.map(relation => React.createElement(
                    RelationTalbe, {
                        relation: relation,
                        fields: relation.fields,
                        key: JSON.stringify(relation)})
                ))
            );
        }
    }


    function updateOrCreate(leftT, rightT, field) {
       return server.updateRelation(leftT, rightT, field)
                    .done(function(resp){
                        var message = "Relation updated between " + leftT + " - "  + rightT;

                        if(resp.status != true) {
                            message = resp.response.message;
                        }
                        snackbar.show(message);
                    });
    }


    return {
        render: function(data, nodeElement) {

            if (!Element) {
                Element = ReactDOM.render(React.createElement(RelationElement,
                    {relations: data}), nodeElement);
                return;
            }

            Element.setState({relations: data});

        }
    };
})();
