function searchSong() {
    const songTitle = document.getElementById('songInput').value;

    // Save the search query to localStorage
    saveSearchHistory(songTitle);
}

function saveSearchHistory(songTitle) {
    let history = JSON.parse(localStorage.getItem('searchHistory')) || [];
    history.push(songTitle);
    localStorage.setItem('searchHistory', JSON.stringify(history));
}

function loadSearchHistory() {
    let history = JSON.parse(localStorage.getItem('searchHistory')) || [];
    let historyDiv = document.getElementById('searchHistory');
    if (history.length > 0) {
        historyDiv.innerHTML = '<h2>Search History:</h2><div class="result-recommend">' +
            history.map(item => `${item}`).join('') +
            '</div>';
    } else {
        historyDiv.innerHTML = '<p>No search history yet</p>';
    }
}

function deleteHistory() {
    // Clear search history from localStorage
    localStorage.removeItem('searchHistory');
    let historyDiv = document.getElementById('searchHistory');
    historyDiv.innerHTML = '<p>Search history cleared!</p>';
}
