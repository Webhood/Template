async function GET(action, parameters = {}) {
	// Create URL builder
	const builder = new URLSearchParams();

	// Generate URL from all parameters
	for (const [key, value] of Object.entries(parameters)) builder.set(key, value);

	// Execute request using fetch
	const response = await fetch(builder.toString() ? `${action}?${builder}` : action, {
		method: "GET",
	});

	// Check response status code
	if (response.status !== 200) throw new Error(await response.text());

	// Return the result
	return await response.json();
}

async function POST(action, parameters = {}) {
	// Execute request using fetch
	const response = await fetch(action, {
		method: "POST",
		body: JSON.stringify(parameters),
		headers: {
			"Content-Type": "application/json",
		},
	});

	// Check response status code
	if (response.status !== 200) throw new Error(await response.text());

	// Return the result
	return await response.json();
}

async function upload(action, parameters = {}) {
	// Create a form body from the parameters
	const body = new FormData();

	// Append all values from parameters
	for (const [name, value] of Object.entries(parameters)) {
		body.append(name, value);
	}

	// Execute request using fetch
	const response = await fetch(action, {
		method: "POST",
		body: body,
	});

	// Check response status code
	if (response.status !== 200) throw new Error(await response.text());

	// Return the result
	return await response.json();
}

function socket(action, callback) {
	// Create websocket object using current location
	const object = new WebSocket((window.location.protocol === "https:" ? "wss://" : "ws://") + window.location.host + action);

	// Add the on-message event listener
	object.onmessage = async (event) => {
		// Call the callback with the data and the object
		await callback(event.data, object);
	};

	// Return the object
	return object;
}

const call = POST;
