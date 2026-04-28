document.addEventListener('DOMContentLoaded', () => {
    const domainInput = document.getElementById('domain-input');
    const searchBtn = document.getElementById('search-btn');
    const btnText = searchBtn.querySelector('.btn-text');
    const btnLoader = searchBtn.querySelector('.btn-loader');
    const resultCard = document.getElementById('search-result');
    
    const resDomain = document.getElementById('res-domain');
    const resStatus = document.getElementById('res-status');
    const resReason = document.getElementById('res-reason');
    
    const statBlocked = document.getElementById('stat-blocked');
    const statAllowed = document.getElementById('stat-allowed');
    const statUpdated = document.getElementById('stat-updated');

    // Fetch initial stats
    fetch('/api/stats')
        .then(res => res.json())
        .then(data => {
            animateNumber(statBlocked, data.total_blocked);
            animateNumber(statAllowed, data.total_allowed);
            statUpdated.textContent = data.last_updated;
        })
        .catch(err => console.error('Error fetching stats:', err));

    searchBtn.addEventListener('click', performSearch);
    domainInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });

    function performSearch() {
        const domain = domainInput.value.trim();
        if (!domain) return;

        // Reset UI
        setLoading(true);
        resultCard.style.display = 'none';

        fetch(`/api/search?domain=${encodeURIComponent(domain)}`)
            .then(res => res.json())
            .then(data => {
                displayResult(data);
            })
            .catch(err => {
                console.error('Search error:', err);
                alert('An error occurred while searching. Please try again.');
            })
            .finally(() => {
                setLoading(false);
            });
    }

    function setLoading(isLoading) {
        if (isLoading) {
            btnText.style.display = 'none';
            btnLoader.style.display = 'block';
            searchBtn.disabled = true;
        } else {
            btnText.style.display = 'block';
            btnLoader.style.display = 'none';
            searchBtn.disabled = false;
        }
    }

    function displayResult(data) {
        resDomain.textContent = data.domain;
        resStatus.textContent = data.status;
        resStatus.className = 'status-badge ' + (data.status === 'blocked' ? 'status-blocked' : 'status-allowed');
        resReason.textContent = data.reason;
        
        resultCard.style.display = 'block';
    }

    function animateNumber(element, target) {
        let current = 0;
        const duration = 1500;
        const stepTime = 20;
        const increment = target / (duration / stepTime);
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                element.textContent = target.toLocaleString();
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current).toLocaleString();
            }
        }, stepTime);
    }
});
