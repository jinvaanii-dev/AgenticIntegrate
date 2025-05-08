import React from 'react';
import { Card, CardBody, Tabs, Tab, Code, Accordion, AccordionItem } from "@nextui-org/react";
import { FiInfo } from 'react-icons/fi';

const ResultPanel = ({ results }) => {
  if (!results) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center text-gray-500 p-4">
        <FiInfo size={48} className="mb-4" />
        <h3 className="text-lg font-medium mb-2">No data to display</h3>
        <p>
          Query HubSpot data to see visualizations and structured results here.
        </p>
      </div>
    );
  }

  // Function to format JSON for display
  const formatJSON = (json) => {
    if (typeof json === 'string') {
      try {
        return JSON.stringify(JSON.parse(json), null, 2);
      } catch (e) {
        return json;
      }
    }
    return JSON.stringify(json, null, 2);
  };

  // Determine if we have contacts, deals, or companies data
  const hasContacts = results.some(item => item.type === 'contacts');
  const hasDeals = results.some(item => item.type === 'deals');
  const hasCompanies = results.some(item => item.type === 'companies');

  return (
    <Tabs aria-label="Data Tabs" color="secondary" variant="bordered">
      {hasContacts && (
        <Tab key="contacts" title="Contacts">
          <Card className="mt-4">
            <CardBody>
              <Accordion>
                {results
                  .filter(item => item.type === 'contacts')
                  .map((contact, index) => (
                    <AccordionItem 
                      key={index} 
                      title={contact.name || `Contact #${index + 1}`}
                      subtitle={contact.email || 'No email'}
                    >
                      <Code block className="text-xs">
                        {formatJSON(contact.data)}
                      </Code>
                    </AccordionItem>
                  ))}
              </Accordion>
            </CardBody>
          </Card>
        </Tab>
      )}
      
      {hasDeals && (
        <Tab key="deals" title="Deals">
          <Card className="mt-4">
            <CardBody>
              <Accordion>
                {results
                  .filter(item => item.type === 'deals')
                  .map((deal, index) => (
                    <AccordionItem 
                      key={index} 
                      title={deal.name || `Deal #${index + 1}`}
                      subtitle={`${deal.amount || 'No amount'} - ${deal.stage || 'No stage'}`}
                    >
                      <Code block className="text-xs">
                        {formatJSON(deal.data)}
                      </Code>
                    </AccordionItem>
                  ))}
              </Accordion>
            </CardBody>
          </Card>
        </Tab>
      )}
      
      {hasCompanies && (
        <Tab key="companies" title="Companies">
          <Card className="mt-4">
            <CardBody>
              <Accordion>
                {results
                  .filter(item => item.type === 'companies')
                  .map((company, index) => (
                    <AccordionItem 
                      key={index} 
                      title={company.name || `Company #${index + 1}`}
                      subtitle={company.domain || 'No domain'}
                    >
                      <Code block className="text-xs">
                        {formatJSON(company.data)}
                      </Code>
                    </AccordionItem>
                  ))}
              </Accordion>
            </CardBody>
          </Card>
        </Tab>
      )}
      
      <Tab key="raw" title="Raw Data">
        <Card className="mt-4">
          <CardBody>
            <Code block className="text-xs max-h-[400px] overflow-auto">
              {formatJSON(results)}
            </Code>
          </CardBody>
        </Card>
      </Tab>
    </Tabs>
  );
};

export default ResultPanel;
