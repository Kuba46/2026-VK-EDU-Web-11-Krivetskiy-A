function getCookie(name) {
	if (!document.cookie) {
		return null;
	}
	const cookies = document.cookie.split(';').map(cookie => cookie.trim());
	for (const cookie of cookies) {
		if (cookie.startsWith(name + '=')) {
			return decodeURIComponent(cookie.substring(name.length + 1));
		}
	}
	return null;
}

function postForm(url, data) {
	const csrftoken = getCookie('csrftoken');
	return fetch(url, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
			'X-CSRFToken': csrftoken || '',
		},
		body: new URLSearchParams(data),
	}).then(async response => {
		const payload = await response.json().catch(() => ({}));
		return { ok: response.ok, status: response.status, payload };
	});
}

function redirectToLogin() {
	const next = encodeURIComponent(window.location.pathname + window.location.search);
	window.location.href = `/login/?next=${next}`;
}

function handleVoteResponse(result, ratingSelector, attrName, id) {
	if (!result.ok) {
		if (result.status === 401) {
			redirectToLogin();
			return;
		}
		alert('Unable to vote right now.');
		return;
	}

	const ratingNode = document.querySelector(`${ratingSelector}[data-${attrName}="${id}"]`);
	if (ratingNode && typeof result.payload.rating !== 'undefined') {
		ratingNode.textContent = result.payload.rating;
	}
}

function disableVoteButtons(selector, attrName, id) {
	const buttons = document.querySelectorAll(`${selector}[data-${attrName}="${id}"]`);
	buttons.forEach(button => {
		button.disabled = true;
	});
}

document.addEventListener('click', event => {
	const questionButton = event.target.closest('.js-question-vote');
	if (questionButton) {
		const questionId = questionButton.dataset.questionId;
		const value = questionButton.dataset.value;
		postForm('/ajax/question/vote/', { question_id: questionId, value })
			.then(result => {
				handleVoteResponse(result, '.js-question-rating', 'question-id', questionId);
				if (result.ok) {
					disableVoteButtons('.js-question-vote', 'question-id', questionId);
				}
			});
		return;
	}

	const answerButton = event.target.closest('.js-answer-vote');
	if (answerButton) {
		const answerId = answerButton.dataset.answerId;
		const value = answerButton.dataset.value;
		postForm('/ajax/answer/vote/', { answer_id: answerId, value })
			.then(result => {
				handleVoteResponse(result, '.js-answer-rating', 'answer-id', answerId);
				if (result.ok) {
					disableVoteButtons('.js-answer-vote', 'answer-id', answerId);
				}
			});
		return;
	}

	const correctButton = event.target.closest('.js-mark-correct');
	if (correctButton) {
		const questionId = correctButton.dataset.questionId;
		const answerId = correctButton.dataset.answerId;
		postForm('/ajax/answer/correct/', { question_id: questionId, answer_id: answerId })
			.then(result => {
				if (!result.ok) {
					if (result.status === 401) {
						redirectToLogin();
						return;
					}
					alert('Unable to mark correct answer.');
					return;
				}
				const allButtons = document.querySelectorAll(`.js-mark-correct[data-question-id="${questionId}"]`);
				allButtons.forEach(button => {
					button.classList.remove('btn-success');
					button.classList.add('btn-outline-success');
				});
				correctButton.classList.remove('btn-outline-success');
				correctButton.classList.add('btn-success');
			});
	}
});
