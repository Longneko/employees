$(document).ready(function(){
    // Vue components:
    // item component
    Vue.component('item', {
        template: '#item-template',
        props: {
            model: Object,
            childrenRef: String,
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
                if ( !this.childrenLoaded ) {
                    for ( var child_id of this.model[this.childrenRef] ) {
                        $.ajax({
                            type: 'POST',
                            url: that.fetchUrl,
                            data: JSON.stringify({
                                id: child_id
                            }),
                            contentType: 'application/json; charset=utf-8', 
                            success: function(data) {
                                that.children.push(data[0])
                            }
                        })
                    }
                }
            }
        }
    });

    // Vue Root element
    var employee_tree = new Vue({
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
