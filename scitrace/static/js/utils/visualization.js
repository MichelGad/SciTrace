/**
 * Data visualization utility functions for SciTrace
 * 
 * Provides common data visualization patterns and helpers.
 */

class VisualizationUtils {
    /**
     * Initialize Vis.js network
     * @param {HTMLElement} container - Container element
     * @param {Object} data - Network data (nodes and edges)
     * @param {Object} options - Network options
     * @returns {Object} - Network instance
     */
    static initNetwork(container, data, options = {}) {
        if (typeof vis === 'undefined') {
            throw new Error('Vis.js library is not loaded');
        }

        const defaultOptions = {
            nodes: {
                shape: 'box',
                margin: 10,
                font: {
                    size: 14,
                    color: '#343a40'
                },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                width: 2,
                color: {
                    color: '#848484',
                    highlight: '#848484'
                },
                smooth: {
                    type: 'continuous'
                },
                arrows: {
                    to: {
                        enabled: true,
                        scaleFactor: 1,
                        type: 'arrow'
                    }
                }
            },
            physics: {
                enabled: true,
                stabilization: {
                    iterations: 100
                }
            },
            interaction: {
                hover: true,
                tooltipDelay: 200
            }
        };

        const networkOptions = { ...defaultOptions, ...options };
        const network = new vis.Network(container, data, networkOptions);

        return network;
    }

    /**
     * Create node data for Vis.js
     * @param {Array} nodes - Array of node objects
     * @returns {Array} - Formatted node data
     */
    static createNodeData(nodes) {
        return nodes.map(node => ({
            id: node.id,
            label: node.label || node.name,
            title: node.description || node.label || node.name,
            color: node.color || this.getDefaultNodeColor(node.type),
            shape: node.shape || 'box',
            size: node.size || 20,
            font: {
                size: node.fontSize || 14,
                color: node.fontColor || '#343a40'
            },
            borderWidth: node.borderWidth || 2,
            shadow: node.shadow !== false,
            ...node
        }));
    }

    /**
     * Create edge data for Vis.js
     * @param {Array} edges - Array of edge objects
     * @returns {Array} - Formatted edge data
     */
    static createEdgeData(edges) {
        return edges.map(edge => ({
            from: edge.from,
            to: edge.to,
            label: edge.label || '',
            title: edge.description || edge.label || '',
            color: edge.color || '#848484',
            width: edge.width || 2,
            arrows: edge.arrows || 'to',
            smooth: edge.smooth || {
                type: 'continuous'
            },
            ...edge
        }));
    }

    /**
     * Get default node color based on type
     * @param {string} type - Node type
     * @returns {Object} - Color object
     */
    static getDefaultNodeColor(type) {
        const colors = {
            'raw_data': { background: '#87CEEB', border: '#4682B4' },
            'preprocessed': { background: '#90EE90', border: '#32CD32' },
            'analysis': { background: '#FFA07A', border: '#FF6347' },
            'modeling': { background: '#DDA0DD', border: '#9370DB' },
            'visualization': { background: '#F0E68C', border: '#DAA520' },
            'scripts': { background: '#4CAF50', border: '#2E7D32' },
            'results': { background: '#FFA07A', border: '#FF6347' },
            'plots': { background: '#DDA0DD', border: '#9370DB' },
            'dataset_root': { background: '#4CAF50', border: '#2E7D32' },
            'default': { background: '#E0E0E0', border: '#9E9E9E' }
        };

        return colors[type] || colors.default;
    }

    /**
     * Create file tree visualization
     * @param {HTMLElement} container - Container element
     * @param {Array} fileTree - File tree data
     * @param {Object} options - Visualization options
     */
    static createFileTree(container, fileTree, options = {}) {
        const defaultOptions = {
            showFiles: true,
            showDirectories: true,
            expandLevel: 2,
            onFileClick: null,
            onDirectoryClick: null
        };

        const opts = { ...defaultOptions, ...options };
        
        const treeHtml = this.buildTreeHtml(fileTree, opts, 0);
        container.innerHTML = treeHtml;

        // Add event listeners
        this.addTreeEventListeners(container, opts);
    }

    /**
     * Build HTML for file tree
     * @param {Array} items - Tree items
     * @param {Object} options - Options
     * @param {number} level - Current level
     * @returns {string} - HTML string
     */
    static buildTreeHtml(items, options, level) {
        let html = '';

        items.forEach(item => {
            const isDirectory = item.type === 'directory';
            const isExpanded = level < options.expandLevel;
            const hasChildren = isDirectory && item.children && item.children.length > 0;
            
            const itemClass = isDirectory ? 'tree-directory' : 'tree-file';
            const iconClass = isDirectory ? 'fas fa-folder' : this.getFileIcon(item.name);
            const sizeInfo = !isDirectory && item.size ? ` (${UiUtils.formatFileSize(item.size)})` : '';

            html += `
                <div class="tree-item" data-level="${level}" data-type="${item.type}" data-path="${item.path}">
                    <div class="tree-item-content ${itemClass}" style="padding-left: ${level * 20 + 10}px;">
                        ${hasChildren ? `
                            <span class="tree-toggle ${isExpanded ? 'expanded' : ''}">
                                <i class="fas fa-chevron-right"></i>
                            </span>
                        ` : '<span class="tree-spacer"></span>'}
                        <i class="${iconClass} me-2"></i>
                        <span class="tree-name">${item.name}${sizeInfo}</span>
                    </div>
                    ${hasChildren && isExpanded ? `
                        <div class="tree-children">
                            ${this.buildTreeHtml(item.children, options, level + 1)}
                        </div>
                    ` : ''}
                </div>
            `;
        });

        return html;
    }

    /**
     * Get file icon based on extension
     * @param {string} filename - File name
     * @returns {string} - Icon class
     */
    static getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const icons = {
            'py': 'fab fa-python',
            'js': 'fab fa-js',
            'html': 'fab fa-html5',
            'css': 'fab fa-css3-alt',
            'json': 'fas fa-code',
            'md': 'fab fa-markdown',
            'txt': 'fas fa-file-alt',
            'csv': 'fas fa-file-csv',
            'pdf': 'fas fa-file-pdf',
            'png': 'fas fa-file-image',
            'jpg': 'fas fa-file-image',
            'jpeg': 'fas fa-file-image',
            'gif': 'fas fa-file-image',
            'svg': 'fas fa-file-image',
            'zip': 'fas fa-file-archive',
            'tar': 'fas fa-file-archive',
            'gz': 'fas fa-file-archive',
            'sql': 'fas fa-database',
            'xml': 'fas fa-file-code',
            'yaml': 'fas fa-file-code',
            'yml': 'fas fa-file-code'
        };

        return icons[ext] || 'fas fa-file';
    }

    /**
     * Add event listeners to file tree
     * @param {HTMLElement} container - Container element
     * @param {Object} options - Options
     */
    static addTreeEventListeners(container, options) {
        // Toggle directory expansion
        container.addEventListener('click', (e) => {
            const toggle = e.target.closest('.tree-toggle');
            if (toggle) {
                const item = toggle.closest('.tree-item');
                const children = item.querySelector('.tree-children');
                
                if (children) {
                    const isExpanded = toggle.classList.contains('expanded');
                    if (isExpanded) {
                        toggle.classList.remove('expanded');
                        children.style.display = 'none';
                    } else {
                        toggle.classList.add('expanded');
                        children.style.display = 'block';
                    }
                }
            }
        });

        // Handle file/directory clicks
        container.addEventListener('click', (e) => {
            const itemContent = e.target.closest('.tree-item-content');
            if (itemContent) {
                const item = itemContent.closest('.tree-item');
                const type = item.dataset.type;
                const path = item.dataset.path;

                if (type === 'file' && options.onFileClick) {
                    options.onFileClick(path, item);
                } else if (type === 'directory' && options.onDirectoryClick) {
                    options.onDirectoryClick(path, item);
                }
            }
        });
    }

    /**
     * Create progress bar
     * @param {HTMLElement} container - Container element
     * @param {number} value - Progress value (0-100)
     * @param {Object} options - Options
     */
    static createProgressBar(container, value, options = {}) {
        const defaultOptions = {
            showPercentage: true,
            animated: true,
            color: 'primary',
            size: 'md',
            striped: false
        };

        const opts = { ...defaultOptions, ...options };
        
        const sizeClass = opts.size === 'sm' ? 'progress-sm' : opts.size === 'lg' ? 'progress-lg' : '';
        const stripedClass = opts.striped ? 'progress-bar-striped' : '';
        const animatedClass = opts.animated ? 'progress-bar-animated' : '';

        container.innerHTML = `
            <div class="progress ${sizeClass}">
                <div class="progress-bar bg-${opts.color} ${stripedClass} ${animatedClass}" 
                     role="progressbar" 
                     style="width: ${value}%"
                     aria-valuenow="${value}" 
                     aria-valuemin="0" 
                     aria-valuemax="100">
                    ${opts.showPercentage ? `${value}%` : ''}
                </div>
            </div>
        `;
    }

    /**
     * Create status badge
     * @param {string} status - Status value
     * @param {Object} options - Options
     * @returns {string} - Badge HTML
     */
    static createStatusBadge(status, options = {}) {
        const defaultOptions = {
            size: 'md',
            pill: false,
            customClass: ''
        };

        const opts = { ...defaultOptions, ...options };
        
        const statusColors = {
            'pending': 'secondary',
            'ongoing': 'warning',
            'done': 'success',
            'completed': 'success',
            'cancelled': 'danger',
            'paused': 'info',
            'low': 'secondary',
            'medium': 'warning',
            'urgent': 'danger',
            'high': 'danger'
        };

        const color = statusColors[status.toLowerCase()] || 'secondary';
        const sizeClass = opts.size === 'sm' ? 'badge-sm' : opts.size === 'lg' ? 'badge-lg' : '';
        const pillClass = opts.pill ? 'rounded-pill' : '';

        return `
            <span class="badge bg-${color} ${sizeClass} ${pillClass} ${opts.customClass}">
                ${status}
            </span>
        `;
    }

    /**
     * Create data table
     * @param {HTMLElement} container - Container element
     * @param {Array} data - Table data
     * @param {Object} options - Options
     */
    static createDataTable(container, data, options = {}) {
        const defaultOptions = {
            columns: null,
            sortable: true,
            searchable: true,
            pagination: true,
            pageSize: 10,
            striped: true,
            hover: true,
            bordered: false
        };

        const opts = { ...defaultOptions, ...options };
        
        if (!data || data.length === 0) {
            container.innerHTML = '<p class="text-muted">No data available</p>';
            return;
        }

        // Auto-generate columns if not provided
        const columns = opts.columns || Object.keys(data[0]);
        
        const tableClass = `table ${opts.striped ? 'table-striped' : ''} ${opts.hover ? 'table-hover' : ''} ${opts.bordered ? 'table-bordered' : ''}`;
        
        let tableHtml = `
            <div class="table-responsive">
                <table class="${tableClass}">
                    <thead>
                        <tr>
                            ${columns.map(col => `<th>${this.formatFieldName(col)}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${data.map(row => `
                            <tr>
                                ${columns.map(col => `<td>${this.formatCellValue(row[col])}</td>`).join('')}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;

        container.innerHTML = tableHtml;
    }

    /**
     * Format cell value for display
     * @param {*} value - Cell value
     * @returns {string} - Formatted value
     */
    static formatCellValue(value) {
        if (value === null || value === undefined) {
            return '<span class="text-muted">-</span>';
        }
        
        if (typeof value === 'boolean') {
            return value ? '<i class="fas fa-check text-success"></i>' : '<i class="fas fa-times text-danger"></i>';
        }
        
        if (typeof value === 'number') {
            return value.toLocaleString();
        }
        
        if (typeof value === 'string' && value.length > 50) {
            return `<span title="${value}">${value.substring(0, 50)}...</span>`;
        }
        
        return value;
    }

    /**
     * Format field name for display
     * @param {string} fieldName - Field name
     * @returns {string} - Formatted field name
     */
    static formatFieldName(fieldName) {
        return fieldName
            .replace(/([A-Z])/g, ' $1')
            .replace(/^./, str => str.toUpperCase())
            .trim();
    }
}

// Export for use in other scripts
window.VisualizationUtils = VisualizationUtils;
