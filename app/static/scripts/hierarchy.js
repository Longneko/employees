var employee_tree

$(document).ready(function(){
    // Vue components:
    // item component
    Vue.component('item', {
        template: '#item-template',
        props: {
            model: Object,
            childrenRef: String,
            parentRef: String,
            fetchUrl: String
        },
        data: function() {
            return {
                open: false,
                children: []
            }
        },
        computed: {
            hasChildren: function() {
                return !!this.model[this.childrenRef].length
            },
            childrenLoaded: function() {
                return !!this.children.length
            }
        },
        methods: {
            toggle: function() {
                if ( this.hasChildren ) {
                    if ( !this.childrenLoaded ) {
                        this.fetchChildren()
                    }
                    this.open = !this.open
                }
            },
            fetchChildren: function() {
                var that = this
                var query = {};
                if ( this.parentRef ) {
                    query[this.parentRef] = this.model.id
                } else {
                    query['id'] = this.model[this.childrenRef]
                }

                if ( !this.childrenLoaded ) {
                    $.ajax({
                        type: 'POST',
                        url: that.fetchUrl,
                        data: JSON.stringify(query),
                        contentType: 'application/json; charset=utf-8', 
                        success: function(data) {
                            that.children = that.children.concat(data)
                        }
                    })
                }
            }
        }
    });

    // Vue Root element
    employee_tree = new Vue({
        el: '#employee-tree',
        data: {
            treeData: []
        },
        mounted() {
            var that = this
            // load top level managers (have no supervisors)
            $.ajax({
                type: 'POST',
                url: EMPLOYEE_FETCH_URL,
                data: JSON.stringify({
                    supervisor_id: null
                }),
                contentType: 'application/json; charset=utf-8', 
                success: function(data) {
                    that.treeData = data
                }
            })
        }
    })
});
