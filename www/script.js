function largeGraphLoad() {
	graphLoad('large');
}

function smallGraphLoad() {
	graphLoad('small');
}

function graphLoad(graphId) {
	// We don't actually care what happens to this. It's only acted upon by
	// event listeners so why give it a variable?
	new GraphParser(graphId)
}

class GraphParser {
	constructor(graphId) {
		this.graph = document.getElementById(graphId).contentDocument;
		this.yearLines = this.parseLegend();
		this.parseGraphLines();
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

			// Why createElementNS? https://stackoverflow.com/a/61236874
			let rect = this.graph.createElementNS('http://www.w3.org/2000/svg', 'rect');

			let yearLine = new YearLine(line, label, rect);

			rect.year = yearLine.year;
			rect.setAttribute('x', patchBounds.x);
			rect.setAttribute('y', patchBounds.y + (rectHeight * i));
			rect.setAttribute('width', patchBounds.width);
			rect.setAttribute('height', rectHeight);
			rect.setAttribute('stroke', 'none');
			rect.setAttribute('fill', 'transparent');

			rect.onclick = this.clickCallback.bind(this);

			legend.appendChild(rect);

			yearLines.push(yearLine);
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

	clickCallback(clickEvent) {
		this.unfocusAll();
		this.setFocus(true, clickEvent.target.year);
	}

	unfocusAll() {
		for (let yearLine of this.yearLines) {
			yearLine.unfocus();
		}
	}

	focusAll() {
		for (let yearLine of this.yearLines) {
			yearLine.focus();
		}
	}

	setFocus(isFocused, year) {
		for (let yearLine of this.yearLines) {
			if (yearLine.year == year) {
				if (isFocused) {
					yearLine.focus();
				} else {
					yearLine.unfocus();
				}
			}
		}
	}
}

class YearLine {
	constructor(legendLine, legendLabel, clickRect) {
		this.legendLine = legendLine;
		this.legendLabel = legendLabel;

		this.year = legendLabel.innerHTML.trim().substr(5, 4);
		this.lineColor = legendLine.style.stroke;

		this.clickRect = clickRect;
	}

	setGraphLine(line) {
		this.graphLine = line;
	}

	unfocus() {
		this.graphLine.style.opacity = "0.1";
		this.legendLine.style.opacity = "0.5";
		this.legendLabel.style.opacity = "0.5";
	}

	focus() {
		this.graphLine.style.opacity = "1";
		this.legendLine.style.opacity = "1";
		this.legendLabel.style.opacity = "1";
	}
}

function updateDate() {
	let date = new Date();
	document.getElementById("currentDate").innerText = `${date.toLocaleDateString()}`;
}