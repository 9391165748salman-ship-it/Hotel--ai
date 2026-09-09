async function updateRequest(id, status) {

    try {

        const response = await fetch(
            `/api/request/${id}/status`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    status: status
                })
            }
        );

        const data = await response.json();

        if (data.success) {

            location.reload();

        }

    } catch (error) {

        alert("Unable to update request.");
    }
}