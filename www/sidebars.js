// @ts-check
/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  docsSidebar: [
    'getting-started',
    'language-guide',
    'cli',
    {
      type: 'category',
      label: 'Library Reference',
      items: [
        'library/overview',
        'library/scores',
        'library/pk',
        'library/lab',
        'library/micro',
        'library/genomics',
        'library/biochem',
        'library/epi',
        'library/nutrition',
        'library/fhir',
        'library/db',
        'library/io',
        'library/finance',
        'library/research',
      ],
    },
    'python-sdk',
    'deployment',
  ],
};

export default sidebars;
