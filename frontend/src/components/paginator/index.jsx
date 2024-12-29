import lodash from "lodash";
import { Button } from "@blueprintjs/core";

function Paginator({ currentPage, totalPages, onPage }) {
    function innerPageRender(items) {
        return lodash.map(items, (n, i) => {
            return (
                <Button
                    key={`item-${i}`}
                    intent={n === currentPage ? "primary" : ""}
                    onClick={() => {
                        onPage(n);
                    }}
                >
                    {n}
                </Button>
            );
        });
    }

    function renderPageList() {
        const maxVisibleButtons = 5; // Maximum number of buttons to display
        let startPage, endPage;

        if (totalPages <= maxVisibleButtons) {
            // All pages fit within the max buttons
            startPage = 1;
            endPage = totalPages;
        } else {
            // Adjust the range when total pages exceed the max buttons
            if (currentPage <= 3) {
                startPage = 1;
                endPage = maxVisibleButtons;
            } else if (currentPage + 2 >= totalPages) {
                startPage = totalPages - maxVisibleButtons + 1;
                endPage = totalPages;
            } else {
                startPage = currentPage - 2;
                endPage = currentPage + 2;
            }
        }

        // Generate the array of pages to display
        const pages = [];
        for (let i = startPage; i <= endPage; i++) {
            pages.push(i);
        }

        return (
            <div className="search-pager">
                <div className="search-pager-buttons">
                    {" Page: "}
                    <Button
                        icon="double-chevron-left"
                        key={`item-start}`}
                        disabled={currentPage == 1}
                        onClick={() => {
                            onPage(1);
                        }}
                    />
                    {totalPages >= 20 ? (
                        <Button
                            icon="chevron-left"
                            key={`item-less10}`}
                            disabled={currentPage <= 10}
                            onClick={() => {
                                onPage(currentPage - 10);
                            }}
                        />
                    ) : (
                        ""
                    )}
                    {innerPageRender(pages)}
                    {totalPages >= 20 ? (
                        <Button
                            icon="chevron-right"
                            key={`item-more10}`}
                            disabled={totalPages - currentPage <= 10}
                            onClick={() => {
                                onPage(currentPage + 10);
                            }}
                        />
                    ) : (
                        ""
                    )}
                    <Button
                        icon="double-chevron-right"
                        key={`item-end}`}
                        disabled={currentPage == totalPages}
                        onClick={() => {
                            onPage(totalPages);
                        }}
                    />
                </div>
            </div>
        );
    }

    return <>{renderPageList()}</>;
}

export default Paginator;
