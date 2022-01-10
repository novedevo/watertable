class GraphParser {
	constructor(graphId) {
		this.graph = document.getElementById(graphId).contentDocument;
		this.yearLines = this.parseLegend();
	}

	parseLegend() {
		let legend = this.graph.getElementById('legend_1');

		// The legend is a weird size so get the patch to find the bounds.
		let patch = this.graph.getElementById('patch_7');
		let patchBounds = patch.getBBox();

		// Each element consists of a line (first) and the year label (second).
		// Subtracting one here to not include the patch
		let lines = (legend.children.length - 1) / 2;

		let rectHeight = patchBounds.height / lines;

		let yearLines = [];
		for (let i = 0; i < lines; ++i) {
			// Adding one here to skip the leading `patch`
			let legendIdx = 1 + (i * 2);

			// We get the group and then the path
			let line = legend.children[legendIdx].children[0];
			let label = legend.children[legendIdx + 1];

			// The comment with the year is positioned predictably
			let year = label.innerHTML.trim().substr(5, 4);
			let lineColor = line.style.stroke;

			// Why createElementNS? https://stackoverflow.com/a/61236874
			let rect = this.graph.createElementNS('http://www.w3.org/2000/svg', 'rect');

			rect.setAttribute('x', patchBounds.x);
			rect.setAttribute('y', patchBounds.y + (rectHeight * i));
			rect.setAttribute('width', patchBounds.width);
			rect.setAttribute('height', rectHeight);
			rect.setAttribute('stroke-width', '1');
			rect.setAttribute('stroke', 'black');
			rect.setAttribute('fill', 'none');

			legend.appendChild(rect);

			yearLines.push(new YearLine(year, lineColor, rect));
		}

		return yearLines;
	}

	parseGraphLines() {
		let axes = this.graph.getElementById('axes_1');

		for (let i = 0; i < this.yearLines.length; ++i) {
			// Before the graph lines is the background for the graph and both
			// axis rule lines
			let axesIdx = 3 + i;

			// Get the group and then the graph line
			let graphLine = axes.children[axesIdx].children[0];
			let graphLineColor = graphLine.style.stroke;

			let foundYearLine = false;
			for (let yearLine of this.yearLines) {
				if (yearLine.lineColor == graphLineColor) {
					yearLine.setGraphLine(graphLine);
					foundYearLine = true;
					break;
				}
			}

			if (!foundYearLine) {
				console.log("Failed to find yearLine for color " + graphLineColor);
			}
		}
	}

	unfocusAll() {
		for (let yearLine of this.yearLines) {
			yearLine.unfocus();
		}
	}
}

class YearLine {
	constructor(year, lineColor, clickRect) {
		this.year = year;
		this.lineColor = lineColor;
		this.clickRect = clickRect;
	}

	setGraphLine(line) {
		this.graphLine = line;
	}

	unfocus() {
		this.graphLine.style.opacity = "0.1";
	}

	focus() {
		this.graphLine.style.opacity = "1";
	}
}