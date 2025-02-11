import { Calendar, momentLocalizer } from "react-big-calendar";
import { useState } from "react";
import moment from "moment";

import "react-big-calendar/lib/css/react-big-calendar.css";

const localizer = momentLocalizer(moment);

export const CalendarPage = () => {
    return (
        <Calendar
            localizer={localizer}
            defaultDate={new Date()}
            defaultView="month"
            events={[
                {
                    start: moment().toDate(),
                    end: moment().toDate(),
                    title: "S.5. - Report",
                    allDay: true,
                    
                },
            ]}
            style={{ height: "100vh" }}
        />
    );
};
