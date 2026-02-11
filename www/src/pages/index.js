import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';
import styles from './index.module.css';

const features = [
  {
    title: '13 Medical Modules',
    description: 'Scores, pharmacokinetics, lab panels, microbiology, genomics, biochemistry, epidemiology, nutrition, FHIR, database, I/O, billing, and research privacy — built in.',
  },
  {
    title: 'English-Like Syntax',
    description: 'Write clinical protocols that read like plain English. No boilerplate, no setup, no framework overhead.',
  },
  {
    title: 'Python SDK',
    description: 'pip install and embed MOISSCode in any Python app. Inject patient data, get structured events back.',
  },
];

function Feature({ title, description }) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center padding-horiz--md padding-vert--lg">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <img src="/MOISSCode/img/moisscode_logo.png" alt="MOISSCode" style={{ width: 280, marginBottom: 16 }} />
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link className="button button--secondary button--lg" to="/docs/getting-started">
            Get Started →
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout title="Home" description="MOISSCode — Medical DSL for clinical decision support">
      <HomepageHeader />
      <main>
        <section className={styles.features}>
          <div className="container">
            <div className="row">
              {features.map((props, idx) => (
                <Feature key={idx} {...props} />
              ))}
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
